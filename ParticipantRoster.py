
import os
import numpy




class ParticipantRoster:

    def __init__(self):

        self.n_participants = 0
        self.names = []
        self.ratings = []
        self.idx = []

        self.opponents = []
        self.current_round_scores = []
        self.all_round_scores = []
        self.total_scores = []

        self.tie_break_scores = []

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

        a = numpy.array([(i, n, -r) for i, (n, r) in enumerate(zip(self.names, self.ratings))], 
                        dtype=[('idx', 'i'), ('name', 'U50'), ('rating', 'i')])

        ii = numpy.sort(a, order=['rating', 'name'])['idx']

        self.names = self.names[ii]
        self.ratings = self.ratings[ii]
        self.idx = numpy.arange(self.n_participants)

    def add_participant(self, name, rating):
        self.n_participants += 1
        self.idx = numpy.arange(self.n_participants)
        self.names = numpy.append(self.names, name)
        self.ratings = numpy.append(self.ratings, rating)
        self.total_scores = numpy.append(self.total_scores, 0)
        self.tie_break_scores = numpy.append(self.tie_break_scores, 0)

        if self.n_participants > 1:
            self._resort_participants()

    def remove_participant(self, idx):
        self.names = numpy.concatenate([self.names[:idx], self.names[idx+1:]])
        self.ratings = numpy.concatenate([self.ratings[:idx], self.ratings[idx+1:]])
        self.total_scores = self.total_scores[:-1]
        self.tie_break_scores = self.tie_break_scores[:-1]
        self.idx = self.idx[:-1]
        self.n_participants -= 1

    def calc_tie_break_scores(self):
        '''
        Calculates and stores the tie-break scores for all participants.
        The tie break score is defined as the sum of the total scores
        of all opponenets a player won against in previous rounds plus
        half of the total scores of all opponents they drew against.
        '''

        for idx in self.idx:

            tie_break_score = 0
            for i_round, score_list in enumerate(self.all_round_scores):

                ###  extracting info from each round
                ###  skip if player was on BYE
                idx_opp = self.opponents[i_round][idx]
                if idx_opp == 'BYE':
                    continue

                result_player = score_list[idx]
                result_opp = score_list[idx_opp]

                if result_player > result_opp:
                    tie_break_score += self.total_scores[idx_opp]
                elif result_player == result_opp:
                    tie_break_score += self.total_scores[idx_opp] / 2.

            self.tie_break_scores[idx] = tie_break_score

    def get_roster_list(self, integer_rating=True):
        '''
        Returns a list of the players, ratings, and scores in a format compatible with PySimpleGUI
        '''
        if integer_rating:
            ratings_tmp = [int(r) for r in self.ratings]
        else:
            ratings_tmp = self.ratings

        return [[idx+1, name, rating] for idx, name, rating in zip(self.idx, self.names, ratings_tmp)]