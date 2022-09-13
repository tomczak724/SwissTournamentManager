
import os
import numpy



class ParticipantRoster:

    def __init__(self):

        self.n_participants = 0
        self.names = []
        self.ratings = []
        self.seeds = []

    def __repr__(self):
        print('\n                        Name  Rating')

        for i in range(self.n_participants):
            ii = self.seeds.tolist().index(i+1)
            row = '%3i' % self.seeds[ii]
            row += '%25s' % self.names[ii]
            row += ' %5i' % self.ratings[ii]
            print(row)

        return ''

    def _resort_participants(self):
        ii = numpy.argsort(self.ratings)
        self.names = self.names[ii][::-1]
        self.ratings = self.ratings[ii][::-1]
        self.seeds = numpy.arange(self.n_participants)+1

    def add_participant(self, name, rating):
        self.n_participants += 1
        self.names = numpy.append(self.names, name)
        self.ratings = numpy.append(self.ratings, rating)
        if self.n_participants > 1:
            self._resort_participants()

    def remove_participant(self, idx):
        self.names = numpy.concatenate([self.names[:idx], self.names[idx+1:]])
        self.ratings = numpy.concatenate([self.ratings[:idx], self.ratings[idx+1:]])
        self.seeds = self.seeds[:-1]
        self.n_participants -= 1

