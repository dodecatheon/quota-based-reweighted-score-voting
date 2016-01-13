## Quota-based Reweighted Score Voting (QRSV), a Droop-proportional PR method
single-winner.

Copyright (C) 2016,  Louis G. "Ted" Stern

This code is an independently reimplemented simplification of Jameson
Quinn's PR-MCA, AKA Approval Threshold Transferable Vote (AT-TV), to
which he retains copyright.

http://www.mail-archive.com/election-methods@lists.electorama.com/msg07066.html

Copyright (C) 2011, Jameson Quinn

The main difference is that while both versions use Score Vote to choose each
winner, my version does not have a different weighting system for the score
vote.

Another minor differences is that I calculate the reweighting factor based on
trunc_sums (see below).

### How QRSV works
 a. Form the set of "standing" candidates.  Candidates whose total score
does not meet a threshold are dropped from the Standing set.
 b. Each ballot is given an initial weight of 1.
 c. The Droop quota equals N / (M + 1), where N is the number of ballots, and
    M is the number of candidates to be seated.
 d. The weighted scores on all ballots are summed for each candidate, giving
    that candidate's toal score.  For each candidate, also keep track of
    "truncated score sums", the weighted scores from ballots that would have
    no more votes if that candidate were seated.
 e. The standing candidate with the highest total score is seated.
 f. Find the seated candidate's Droop graded approval threshold -- the
    maximum score such that the weighted sum of all scores at or above that
    threshold exceed one Droop quota of votes.  Set T = the total weighted sum
    of ballots at or above that threshold.
 g. Reweight each ballot by 1 - (Q - L) / (T - L), where Q is the Droop Quota,
    L is the truncated sum for the graded approval threshold, and T is the
    graded approval threshold total.
 h. Repeat steps d through g until M candidates have been seated.

### Simplified version of the method
 a. Each voter casts a ballot rating candidates from 0 to 9 (say).
 b. Sum up the scores for each candidate based on each ballot's weight.
 c. Seat the candidate with the highest weighted score.
 d. Reweight ballots based on how much each ballot approved of the winner
 above the required quota.
 e. Repeat from step b until all seats are filled.

### Name of Method -- QRSV
Like Warren Smith's
[Reweighted Range Voting](http://rangevoting.org/RRV.html), QRSV chooses
winners based on a ratings (AKA Range or Score) ballot, and reweights each
ballot based on a measure of how much of a voice the voter had in selecting
the last winner.  Unlike RRV, that measure is based on meeting a minimum Droop
quota of representation:  1 / (Number of seats + 1).

When compared to RRV, QRSV seats a similar set of winners for the first few
seats, but tends not to discount ballots that choose the most popular
candidates as much, giving more voice to diverse groups.

A disadvantage of the quota-based approach is that it is possible to get
Alabama paradox effects based on the number of seats -- adding one more seat
may sometimes decrease the voting power of a faction.

Both methods are subject to Hylland Free Riding, where a voter may not include
their preferred candidate, knowing they will probably be elected by other
voters anyway, in order to ensure that a lesser-approved candidate is also
chosen.  However, that is ameliorated to some extent by the truncated sum
correction.

### Comparison to Single Transferable Vote
QRSV is similar to Single Transferable Vote (STV), with equal ranking allowed, but there are
some key differences:

In standard STV,
* There must be exactly one candidate at each rank.
* There can be no gaps in ranks, though lower ranks do not have to be filled in.
* The only way for lower ranked candidates to be counted is for candidates in higher ranks to be eliminated or seated, at which time lower ranks are moved up one rank.
* When no candidate's score exceeds the quota, the only way to
increase the vote strength of other candidates is to eliminate the
candidate with lowest top-rank score and move other candidates on
that ballot up one rank.

In QRSV,
* Equal *rating* is allowed.
* It is not necessary to fill in a candidate for each *rating* level.
* Top rating is measured by total score.

This decreases strategic voting incentives when compared to STV.

### Background:

A similar Bucklin Transferable Vote idea described by Abd ul-Rahman
Lomax in this post, but he followed the STV approach of upranking when
a candidate was seated and reverted to Asset voting for the last seat
if no candidate makes the quota.

http://lists.electorama.com/pipermail/election-methods-electorama.com/2010-March/025738.html

However even if ER-Bucklin simply used a straight approval threshold, it would
fail the Participation and Independence from Irrelevant Alternatives criteria
for a single-winner (PC and IIAC).  By using score vote to choose individual
seat winners, we satisfy PC and IIAC.

Both QRSV and STV transfer would make the same over-quota transfer
[(candidate_total - quota)/candidate_total], but I include an extra
correction to take account of truncated ballots:

    over-vote rescale factor = 1 - ((Q - L) / (T - L)),
                               constrained to be between 0.0 and 1.0

Glossary, following the analogy of musical chairs:

Seated:      A candidate has met the quota and won a seat.

Standing:    Candidate has not met quota and is still in the running.

Truncated:   A candidate's vote becomes truncated on a single ballot when the
             ballot has only one standing candidate left.

             If that single candidate is seated, there are no other
             candidates to transfer the overquota vote to.

             If a candidate's score is truncated on a ballot on the first
             round, the ballot is called a bullet vote -- the voter
             picked a single candidate.

             But it can also happen when all other choices on the
             ballot have already been seated.  Then if candidate A
             receives an overvote and the ballot is removed entirely,
             the ballot's excess score for A is not transferable.

Trunc_Sums:  The sum of truncated scores for a candidate determine how much
             of the candidate's total score can be rescaled and
             redistributed in the event of being seated with an overquota.
             If the total approved score for the candidate is T, the quota
             is Q, and the candidate's trunc_sum is L [denoting that the
             truncation leads to a _L_ocking of the ballot], the over-vote
             rescaling is

	         1 - (Q-L)/(T-L)

	     for Q > L and T > L.  We constrain the quotient term to lie
	     between 0.0 and 1.0, so if either the total score is
	     truncated, or the amount of truncation is greater than the
	     quota, there is no over-vote left to be transferred.

Rescaled
weight:      As ballots "get their way" by seating a candidate with a
             total approval score over the quota, we multiply the weight
             of that ballot by a factor to transfer the over-quota portion
             of the vote to other candidates on that ballot.

Approval
Threshold
Score:       We accumulate the total rescaled weight of ballots that vote
             for each candidate at each non-zero score level.

             The Total Approval score is the total weight of votes for a
             candidate at or above a specific rating.

             The Approval threshold is the rating at which one or more
             candidates has a Total Approval Score that exceeds the quota, and
             once one candidate has exceeded the quota, the Total Approval
             scores of all candidates are called their Bucklin Scores.

### Usage
Here's how to run the various examples:

June 2011 example from
http://rangevoting.org/June2011RealWorldRRVvotes.txt
```
  ./qrsv.py -n 9 -m 9 -i june2011.csv -o june2011_output.csv
```
Stephen Unger's STV example, from http://rangevoting.org/STVPRunger.html
```
  ./qrsv.py -n 3 -m 4 -i unger.csv -o unger_output.csv
```
A sample ballot from the CTV project:
```
  ./qrsv.py -n 5 -m 10 -i new_sample.csv -o new_sample_output.csv
```
The csv output file contains a table with the intermediate Bucklin scores as
the score level is lowered to the threshold.  Each score is listed as
```
   #.#### (position)
```
where the number in parentheses is the rank of the Bucklin score.  If the
score with rank (1) exceeds the quota, that candidate is seated.

#### Excluding candidates

You can test an election with one or more candidates excluded using the Unix
tool 'cut'.  Here's the first example, excluding candidate '108':
```
  cut -f1-7,8- -d, june2011.csv | \
  ./qrsv.py -n 9 -m 9 -i - -o june2011_excluding_108_output.csv

Running the code:

If you don't have a python interpreter, you can run the code via the web,
using

   http://ideone.com

Select Python from the left sidebar.

Cut and paste everything in the qrsv.py file, from from the "BEGIN cut and
paste line" (around line 27) to "END cut and paste line" (around line 404),
and insert it into the web page's source code textarea.

In the very same textarea, following the source you've just cut and pasted
above, enter the appropriate input to run your example.  To run the
june2011.csv input, for example, you enter the following two statements:

```
election = Election(nseats=9,
                    max_score=9,
                    csv_input='-',
                    csv_output='-',
                    qtype='droop')

election.run_election()
```

Click where it says ```click here to enter input (stdin) ...```, and paste in
your comma-separated variable input.  For this example, use text from the
june2011.csv file.

Then click on the Submit button on the lower left.
