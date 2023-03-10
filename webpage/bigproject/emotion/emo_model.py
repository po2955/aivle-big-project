import tensorflow_addons as tfa
from transformers import PreTrainedTokenizer
from shutil import copyfile
import unicodedata
from transformers import *
import logging
#from tqdm import tqdm
#import pandas as pd
import numpy as np
import tensorflow as tf
from google.cloud import speech
import wave
#from six.moves import queue
import pyaudio
import io
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "emotion/files/celtic-bazaar-308312-c7617526e30e.json"


def recode(path, filename, seconds):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = seconds
    WAVE_OUTPUT_FILENAME = path + filename + ".wav"

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Start to record the audio.")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Recording is finished.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


def google_STT(path, filename):
    speech_file = path + filename + ".wav"
    client = speech.SpeechClient()

    with io.open(speech_file, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED,
        sample_rate_hertz=44100,
        language_code="ko-KR",
        audio_channel_count=1
    )

    response = client.recognize(config=config, audio=audio)

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        print("Transcript: {}".format(result.alternatives[0].transcript))
        return result.alternatives[0].transcript
    # return response.results[0].alternatives[0].transcript


def sentiment_analysis(sentence, model_path):
    logger = logging.getLogger(__name__)

    VOCAB_FILES_NAMES = {"vocab_file": "tokenizer_78b3253a26.model",
                         "vocab_txt": "vocab.txt"}

    PRETRAINED_VOCAB_FILES_MAP = {
        "vocab_file": {
            "monologg/kobert": "https://s3.amazonaws.com/models.huggingface.co/bert/monologg/kobert/tokenizer_78b3253a26.model",
            "monologg/kobert-lm": "https://s3.amazonaws.com/models.huggingface.co/bert/monologg/kobert-lm/tokenizer_78b3253a26.model",
            "monologg/distilkobert": "https://s3.amazonaws.com/models.huggingface.co/bert/monologg/distilkobert/tokenizer_78b3253a26.model"
        },
        "vocab_txt": {
            "monologg/kobert": "https://s3.amazonaws.com/models.huggingface.co/bert/monologg/kobert/vocab.txt",
            "monologg/kobert-lm": "https://s3.amazonaws.com/models.huggingface.co/bert/monologg/kobert-lm/vocab.txt",
            "monologg/distilkobert": "https://s3.amazonaws.com/models.huggingface.co/bert/monologg/distilkobert/vocab.txt"
        }
    }

    PRETRAINED_POSITIONAL_EMBEDDINGS_SIZES = {
        "monologg/kobert": 512,
        "monologg/kobert-lm": 512,
        "monologg/distilkobert": 512
    }

    PRETRAINED_INIT_CONFIGURATION = {
        "monologg/kobert": {"do_lower_case": False},
        "monologg/kobert-lm": {"do_lower_case": False},
        "monologg/distilkobert": {"do_lower_case": False}
    }

    SPIECE_UNDERLINE = u'???'

    class KoBertTokenizer(PreTrainedTokenizer):
        """
            SentencePiece based tokenizer. Peculiarities:
                - requires `SentencePiece <https://github.com/google/sentencepiece>`_
        """
        vocab_files_names = VOCAB_FILES_NAMES
        pretrained_vocab_files_map = PRETRAINED_VOCAB_FILES_MAP
        pretrained_init_configuration = PRETRAINED_INIT_CONFIGURATION
        max_model_input_sizes = PRETRAINED_POSITIONAL_EMBEDDINGS_SIZES

        def __init__(
                self,
                vocab_file,
                vocab_txt,
                do_lower_case=False,
                remove_space=True,
                keep_accents=False,
                unk_token="[UNK]",
                sep_token="[SEP]",
                pad_token="[PAD]",
                cls_token="[CLS]",
                mask_token="[MASK]",
                **kwargs):
            super().__init__(
                unk_token=unk_token,
                sep_token=sep_token,
                pad_token=pad_token,
                cls_token=cls_token,
                mask_token=mask_token,
                **kwargs
            )

            # Build vocab
            self.token2idx = dict()
            self.idx2token = []
            with open(vocab_txt, 'r', encoding='utf-8') as f:
                for idx, token in enumerate(f):
                    token = token.strip()
                    self.token2idx[token] = idx
                    self.idx2token.append(token)

            try:
                import sentencepiece as spm
            except ImportError:
                logger.warning("You need to install SentencePiece to use KoBertTokenizer: https://github.com/google/sentencepiece"
                               "pip install sentencepiece")

            self.do_lower_case = do_lower_case
            self.remove_space = remove_space
            self.keep_accents = keep_accents
            self.vocab_file = vocab_file
            self.vocab_txt = vocab_txt

            self.sp_model = spm.SentencePieceProcessor()
            self.sp_model.Load(vocab_file)

        @property
        def vocab_size(self):
            return len(self.idx2token)

        def get_vocab(self):
            return dict(self.token2idx, **self.added_tokens_encoder)

        def __getstate__(self):
            state = self.__dict__.copy()
            state["sp_model"] = None
            return state

        def __setstate__(self, d):
            self.__dict__ = d
            try:
                import sentencepiece as spm
            except ImportError:
                logger.warning("You need to install SentencePiece to use KoBertTokenizer: https://github.com/google/sentencepiece"
                               "pip install sentencepiece")
            self.sp_model = spm.SentencePieceProcessor()
            self.sp_model.Load(self.vocab_file)

        def preprocess_text(self, inputs):
            if self.remove_space:
                outputs = " ".join(inputs.strip().split())
            else:
                outputs = inputs
            outputs = outputs.replace("``", '"').replace("''", '"')

            if not self.keep_accents:
                outputs = unicodedata.normalize('NFKD', outputs)
                outputs = "".join(
                    [c for c in outputs if not unicodedata.combining(c)])
            if self.do_lower_case:
                outputs = outputs.lower()

            return outputs

        def _tokenize(self, text, return_unicode=True, sample=False):
            """ Tokenize a string. """
            text = self.preprocess_text(text)

            if not sample:
                pieces = self.sp_model.EncodeAsPieces(text)
            else:
                pieces = self.sp_model.SampleEncodeAsPieces(text, 64, 0.1)
            new_pieces = []
            for piece in pieces:
                if len(piece) > 1 and piece[-1] == str(",") and piece[-2].isdigit():
                    cur_pieces = self.sp_model.EncodeAsPieces(
                        piece[:-1].replace(SPIECE_UNDERLINE, ""))
                    if piece[0] != SPIECE_UNDERLINE and cur_pieces[0][0] == SPIECE_UNDERLINE:
                        if len(cur_pieces[0]) == 1:
                            cur_pieces = cur_pieces[1:]
                        else:
                            cur_pieces[0] = cur_pieces[0][1:]
                    cur_pieces.append(piece[-1])
                    new_pieces.extend(cur_pieces)
                else:
                    new_pieces.append(piece)

            return new_pieces

        def _convert_token_to_id(self, token):
            """ Converts a token (str/unicode) in an id using the vocab. """
            return self.token2idx.get(token, self.token2idx[self.unk_token])

        def _convert_id_to_token(self, index, return_unicode=True):
            """Converts an index (integer) in a token (string/unicode) using the vocab."""
            return self.idx2token[index]

        def convert_tokens_to_string(self, tokens):
            """Converts a sequence of tokens (strings for sub-words) in a single string."""
            out_string = "".join(tokens).replace(SPIECE_UNDERLINE, " ").strip()
            return out_string

        def build_inputs_with_special_tokens(self, token_ids_0, token_ids_1=None):
            """
            Build model inputs from a sequence or a pair of sequence for sequence classification tasks
            by concatenating and adding special tokens.
            A KoBERT sequence has the following format:
                single sequence: [CLS] X [SEP]
                pair of sequences: [CLS] A [SEP] B [SEP]
            """
            if token_ids_1 is None:
                return [self.cls_token_id] + token_ids_0 + [self.sep_token_id]
            cls = [self.cls_token_id]
            sep = [self.sep_token_id]
            return cls + token_ids_0 + sep + token_ids_1 + sep

        def get_special_tokens_mask(self, token_ids_0, token_ids_1=None, already_has_special_tokens=False):
            """
            Retrieves sequence ids from a token list that has no special tokens added. This method is called when adding
            special tokens using the tokenizer ``prepare_for_model`` or ``encode_plus`` methods.
            Args:
                token_ids_0: list of ids (must not contain special tokens)
                token_ids_1: Optional list of ids (must not contain special tokens), necessary when fetching sequence ids
                    for sequence pairs
                already_has_special_tokens: (default False) Set to True if the token list is already formated with
                    special tokens for the model
            Returns:
                A list of integers in the range [0, 1]: 0 for a special token, 1 for a sequence token.
            """

            if already_has_special_tokens:
                if token_ids_1 is not None:
                    raise ValueError(
                        "You should not supply a second sequence if the provided sequence of "
                        "ids is already formated with special tokens for the model."
                    )
                return list(map(lambda x: 1 if x in [self.sep_token_id, self.cls_token_id] else 0, token_ids_0))

            if token_ids_1 is not None:
                return [1] + ([0] * len(token_ids_0)) + [1] + ([0] * len(token_ids_1)) + [1]
            return [1] + ([0] * len(token_ids_0)) + [1]

        def create_token_type_ids_from_sequences(self, token_ids_0, token_ids_1=None):
            """
            Creates a mask from the two sequences passed to be used in a sequence-pair classification task.
            A KoBERT sequence pair mask has the following format:
            0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 1
            | first sequence    | second sequence
            if token_ids_1 is None, only returns the first portion of the mask (0's).
            """
            sep = [self.sep_token_id]
            cls = [self.cls_token_id]
            if token_ids_1 is None:
                return len(cls + token_ids_0 + sep) * [0]
            return len(cls + token_ids_0 + sep) * [0] + len(token_ids_1 + sep) * [1]

        def save_vocabulary(self, save_directory):
            """ Save the sentencepiece vocabulary (copy original file) and special tokens file
                to a directory.
            """
            if not os.path.isdir(save_directory):
                logger.error(
                    "Vocabulary path ({}) should be a directory".format(save_directory))
                return

            # 1. Save sentencepiece model
            out_vocab_model = os.path.join(
                save_directory, VOCAB_FILES_NAMES["vocab_file"])

            if os.path.abspath(self.vocab_file) != os.path.abspath(out_vocab_model):
                copyfile(self.vocab_file, out_vocab_model)

            # 2. Save vocab.txt
            index = 0
            out_vocab_txt = os.path.join(
                save_directory, VOCAB_FILES_NAMES["vocab_txt"])
            with open(out_vocab_txt, "w", encoding="utf-8") as writer:
                for token, token_index in sorted(self.token2idx.items(), key=lambda kv: kv[1]):
                    if index != token_index:
                        logger.warning(
                            "Saving vocabulary to {}: vocabulary indices are not consecutive."
                            " Please check that the vocabulary is not corrupted!".format(
                                out_vocab_txt)
                        )
                        index = token_index
                    writer.write(token + "\n")
                    index += 1

            return out_vocab_model, out_vocab_txt

    global tokenizer
    tokenizer = KoBertTokenizer.from_pretrained('monologg/kobert')

    def create_sentiment_bert():
        # ?????? pretrained ?????? ??????
        model = TFBertModel.from_pretrained("monologg/kobert", from_pt=True)
        # ?????? ??????, ????????? ??????, ???????????? ?????? ??????
        token_inputs = tf.keras.layers.Input(
            (SEQ_LEN,), dtype=tf.int32, name='input_word_ids')
        mask_inputs = tf.keras.layers.Input(
            (SEQ_LEN,), dtype=tf.int32, name='input_masks')
        segment_inputs = tf.keras.layers.Input(
            (SEQ_LEN,), dtype=tf.int32, name='input_segment')
        # ????????? [??????, ?????????, ????????????]??? ?????? ??????
        bert_outputs = model([token_inputs, mask_inputs, segment_inputs])

        bert_outputs = bert_outputs[1]
        sentiment_first = tf.keras.layers.Dense(
            1, activation='sigmoid', kernel_initializer=tf.keras.initializers.TruncatedNormal(0.02))(bert_outputs)
        sentiment_model = tf.keras.Model(
            [token_inputs, mask_inputs, segment_inputs], sentiment_first)
        # ?????????????????? ???????????? Adam ??????????????? ??????
        sentiment_model.compile(optimizer=opt, loss=tf.keras.losses.BinaryCrossentropy(),
                                metrics=['accuracy'])
        return sentiment_model

    SEQ_LEN = 128

    # Rectified Adam ??????????????? ??????
    opt = tfa.optimizers.RectifiedAdam(
        lr=1.0e-5, weight_decay=0.0025, warmup_proportion=0.05)

    model = create_sentiment_bert()

    model.load_weights(model_path)

    tf.get_logger().setLevel(logging.ERROR)

    def sentence_convert_data(data):
        global tokenizer
        tokens, masks, segments = [], [], []
        token = tokenizer.encode(
            data, max_length=SEQ_LEN, truncation=True, padding='max_length')

        num_zeros = token.count(0)
        mask = [1]*(SEQ_LEN-num_zeros) + [0]*num_zeros
        segment = [0]*SEQ_LEN

        tokens.append(token)
        segments.append(segment)
        masks.append(mask)

        tokens = np.array(tokens)
        masks = np.array(masks)
        segments = np.array(segments)
        return [tokens, masks, segments]

    def evaluation_predict(sentence):
        data_x = sentence_convert_data(sentence)
        predict = model.predict(data_x)
        predict_value = np.ravel(predict)
        predict_answer = np.round(predict_value, 0).item()

        if predict_answer == 0:
            print("(?????? ?????? : %.2f) ???????????? ???????????????." % (1-predict_value))
        elif predict_answer == 1:
            print("(?????? ?????? : %.2f) ???????????? ???????????????." % predict_value)

        return predict[0][0]

    return evaluation_predict(sentence)