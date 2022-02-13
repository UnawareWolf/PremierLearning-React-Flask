from dataclasses import dataclass
from typing import List
import numpy
import sys

from keras.models import Sequential
from keras.layers import Dense

from premierlearning.clean_match import CleanMatch, get_inputs_from_data_key, get_outputs_from_data_key


@dataclass
class MLOptions:
    reps: int
    epochs: int
    batch_size: int
    input_keys: list
    output_key: str

EPOCHS = 8
BATCH_SIZE = 32
REPS = 4
if '--quick' in sys.argv:
    EPOCHS = 2
    REPS = 2


class MLData:

    def __init__(self, clean_matches: List[CleanMatch], input_to_pred, input_keys, output_key, include_standard_stats):
        self.input_learn = numpy.array(get_inputs_from_data_key(clean_matches, input_keys, include_standard_stats)).astype(float)
        self.output_learn = numpy.array(get_outputs_from_data_key(clean_matches, output_key)).astype(float)
        self.input_to_pred = numpy.array(get_inputs_from_data_key(input_to_pred, input_keys, include_standard_stats)).astype(float)
        
        self.model = Sequential()
        self.model.add(Dense(self.input_learn.shape[1], input_dim=self.input_learn.shape[1], activation='relu'))
        self.model.add(Dense(10, activation='relu'))
        self.model.add(Dense(1))
        self.model.compile(loss=loss_func, optimizer='adam')
    
    
    def get_predictions(self):
        history = self.model.fit(self.input_learn, self.output_learn,
            epochs=EPOCHS, batch_size=BATCH_SIZE,
            verbose=0)

        return self.model.predict(self.input_to_pred), history.history['loss'][-1]


def loss_func(y_true, y_pred):
        y_true = float(y_true)
        y_pred = float(y_pred)

        return abs(y_true - y_pred) ** 2


def get_avg_predictions(clean_matches, input_pred, input_keys, output_key, include_standard_stats):
        print('Getting predictions for %s...' % output_key)
        is_quick = '--quick' in sys.argv
        if is_quick:
            print("(quick run)")
        ml_data = MLData(clean_matches, input_pred, input_keys, output_key, include_standard_stats)

        preds_and_loss = []
        for _ in range(REPS):
            preds_and_loss.append(ml_data.get_predictions())

        min_loss = min(m[1] for m in preds_and_loss)

        model_predictions = [m[0] for m in preds_and_loss if m[1] <= min_loss * 1.2]

        averaged_predictions = []
        for i in range(len(model_predictions[0])):
            single_match_predictions = []
            for prediction_array in model_predictions:
                single_match_predictions.append(prediction_array[i])
            averaged_predictions.append(sum(single_match_predictions) / len(single_match_predictions))

        return averaged_predictions
