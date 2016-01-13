import itertools

def ncycles(iterable, n):
    "Returns the sequence elements n times"
    return itertools.chain.from_iterable(itertools.repeat(tuple(iterable), n))

def parse_one_vote(vote_txt):
    try:
        return int(vote_txt)
    except ValueError:
        return -1 #Effectively equal to 0. Not doing

def reweight_factor(before, factor):
    """
    Returns tuple (diff, after)
    """
    after = before * factor
    return (before - after, after)
    
class Ballot:
    def __init__(self, text, cnames):
        cols = text.split()
        self.name = cols[0]
        self.vote_list = [parse_one_vote(vote) for vote in cols[1:]]
        self.len = len(cnames)
        assert len(self.vote_list) == self.len
        self.vote_dict = dict(zip(cnames, self.vote_list))
        
    def start_round(self, round_cutoff):
        self.round_score_weight = 1.0
        self.round_droop_weight = 1.0
        self.round_approval = [(1.0 if vote >= round_cutoff else 0.0) for vote in self.vote_list]
        return self.round_approval
        
    def reweight_droop_for(self, factor, c_ind):
        if self.round_approval[c_ind]:
            diff, self.round_droop_weight = reweight_factor(self.round_droop_weight, factor)
            if c_ind == 11:
                print "reweighting", factor, self.round_approval[11], [(diff * approval) for approval in self.round_approval]
            return [(diff * approval) for approval in self.round_approval]
        else:
            return False #[0.0] * self.len
    
    def reweight_score_for(self, factor, c_ind):
        if self.round_approval[c_ind]:
            diff, self.round_score_weight = reweight_factor(self.round_score_weight, factor)
            return [(diff * approval) for approval in self.round_approval]
        else:
            return False #[0.0] * self.len
    
class Election:
    def __init__(self, lines, seats, times=1):
        lines = iter(lines)
        self.seats = seats
        self.cnames = lines.next().split()[1:]
        if times > 1:
            lines = ncycles(lines, times)
        self.c_indexes = dict([(name, n) for n, name in enumerate(self.cnames)])
        self.ballots = [Ballot(line, self.cnames) for line in lines]
        self.droop_size = float(len(self.ballots)) / (seats + 1.0)
        
    def do_election(self, max_level):
        level = max_level
        winners = []
        while level > 0:
            winners += self.do_round(level, winners, level==1)
            level -= 1
        return winners
    
    def do_round(self, round_cutoff, pre_elected_names, leftovers=False):
        print "Doing round.", round_cutoff, pre_elected_names
        new_winners = []
        starting_scores = [sum(scores) for scores in zip(*[ballot.start_round(round_cutoff) for ballot in self.ballots])]
        print "Starting scores:", starting_scores
        scores = list(starting_scores) #pass by reference, modified in place
        droop = list(starting_scores) #pass by reference, modified in place
        for elected_name in pre_elected_names:
            self.reweight_for(elected_name, droop, Ballot.reweight_droop_for)
        print "Starting droops:", droop
        while len(new_winners) + len(pre_elected_names) < self.seats:
            winner = self.elect_one(scores, droop, leftovers)
            if winner:
                print "Elected ", winner, scores, droop
                new_winners.append(winner)
            else:
                break
        if len(pre_elected_names) and len(new_winners) + len(pre_elected_names) == self.seats:
            losers = zip(droop, self.cnames)
            losers.sort()
            losers.reverse()
            print "LOSERS: ", losers
#        if leftovers:
#            losers = []
#            loser = True
#            print "pre-loser droop:", droop, scores
#            while loser and max(droop) > 0:
#                print "max loser score:", max(droop)
#                loser = self.elect_one(scores, droop, leftovers)
#                print "Elected loser ", loser, scores, droop
#                losers.append(loser)
#                print "post max loser score:", max(droop), loser, droop
#            print "LOSERS:", losers
        return new_winners
    
    def reweight_for(self, elected_name, droop_or_score, reweight_method, leftovers=False):
        i = self.c_indexes[elected_name]
        if droop_or_score[i] > 0:
            factor = (droop_or_score[i] - self.droop_size) / droop_or_score[i]
            for ballot in self.ballots:
                adjustments = reweight_method(ballot, factor, i)
                if adjustments:
                    for j, diff in enumerate(adjustments):
                        if droop_or_score[j]:
                            droop_or_score[j] -= diff
                        if leftovers and droop_or_score[j] < 0:
                            droop_or_score[j] = 0
                        assert droop_or_score[j] >= 0
        else:
            print "Elected ineligible?", i, droop_or_score
            raise Exception("ineligible")
        droop_or_score[i] = 0.0 #prevent re-election
                
    def elect_one(self, scores, droop, leftovers=False):
        filtered_scores = self.filter_scores(scores, droop)
        if filtered_scores: #filter sets it to none when there aren't any
            combined_scores = zip(filtered_scores, droop)
            winner_i = combined_scores.index(max(combined_scores)) #max() automatically sorts by first item, then by second
            print "valid winner", winner_i, scores[winner_i], droop[winner_i], filtered_scores[winner_i], filtered_scores
            winner = self.cnames[winner_i]
            self.reweight_for(winner, scores, Ballot.reweight_score_for)
            self.reweight_for(winner, droop, Ballot.reweight_droop_for)
            return winner
        elif leftovers:
            winner_i = droop.index(max(droop))
            winner = self.cnames[winner_i]
            print "leftover", winner_i
            self.reweight_for(winner, droop, Ballot.reweight_droop_for, leftovers)
            return winner
        
    def filter_scores(self, scores, droop):
        result = [(score if adroop >= self.droop_size else 0.0) for score, adroop in zip(scores, droop)]
        if max(result) > 0:
            return result
        else:
            return None