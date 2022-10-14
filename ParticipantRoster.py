
import os
import numpy




class ParticipantRoster:

    def __init__(self):

        self.n_participants = 0
        self.names = []
        self.ratings = []
        self.idx = []

        self.opponents = []
        self.round_scores = []
        self.total_scores = []

        self.all_prev_pairings = []




    def __repr__(self):
        print('\n                        Name  Rating')

        for i in range(self.n_participants):
            ii = self.idx.tolist().index(i)
            row = '%3i' % (self.idx[ii]+1)
            row += '%25s' % self.names[ii]
            row += ' %5i' % self.ratings[ii]
            print(row)

        return ''

    def _resort_participants(self):
        ii = numpy.argsort(self.ratings)
        self.names = self.names[ii][::-1]
        self.ratings = self.ratings[ii][::-1]
        self.idx = numpy.arange(self.n_participants)

    def add_participant(self, name, rating):
        self.n_participants += 1
        self.names = numpy.append(self.names, name)
        self.ratings = numpy.append(self.ratings, rating)
        self.total_scores = numpy.append(self.total_scores, 0)

        if self.n_participants > 1:
            self._resort_participants()

    def remove_participant(self, idx):
        self.names = numpy.concatenate([self.names[:idx], self.names[idx+1:]])
        self.ratings = numpy.concatenate([self.ratings[:idx], self.ratings[idx+1:]])
        self.total_scores = self.total_scores[:-1]
        self.idx = self.idx[:-1]
        self.n_participants -= 1

