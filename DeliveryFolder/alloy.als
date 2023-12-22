sig DateTime {
  timeStamp: one Int
}
sig File {}

abstract sig Bool {}
one sig True, False extends Bool {}

abstract sig User {
  email: one String,
  firstName: one String,
  lastName: one String
}

sig Student extends User {
  invitations: set Invitation,
  scores: set Score
}

sig Educator extends User {
  manages: set Tournament
}

sig Tournament {
  registrationDeadline: one DateTime,
  startingDate: one DateTime,
  ranking: one Ranking,
  battles: set Battle
}

sig Invitation {
  link: one String,
  expirationDate: one DateTime,
  accepted: one Bool,
  team: one Team,
  student: one Student
}

sig Score {
  student: one Student,
  evaluation: one Evaluation,
  value: one Int
}

sig Evaluation {}

sig Ranking {
  tournament: one Tournament,
  scores: set Score
}

sig Team {
  members: some Student,
  submissions: set Submission,
  battle: one Battle
}

sig Battle {
  registrationDeadline: one DateTime,
  submissionDeadline: one DateTime,
  maxStudentsPerTeam: one Int,
  minStudentsPerTeam: one Int,
  teams: set Team,
  repository: one Repository
}

sig Repository {
  link: one String,
  codeKata: one CodeKata
}

sig CodeKata {
  description: one String,
  buildingScripts: set File,
  testCases: set File
}

sig Submission {
  team: one Team,
  forkedRepository: one ForkedRepository
}

sig ForkedRepository extends Repository {}


/////

fact uniqueInvitations {
	no disj s1, s2: Student | s1.invitations & s2.invitations != none
}

fact teamCompetesInABattle {
	all t: Team | some b: Battle | t in b.teams
}

fact battleBelongToTournament {
	all b: Battle | one t: Tournament | b in t.battles
}

fact SubmissionBelongsToOneRepository {
	all s: Submission | one r: Repository | s.forkedRepository = r
}

fact scoreBelongsToOneStudentOneEvaluation {
	all s: Score | one s.student and one s.evaluation
}

fact rankingBelongsToTournamentAndScores {
	all r: Ranking | one r.tournament and some r.scores
}

fact tournamentHasUniqueRanking {
	all disj t1, t2: Tournament | t1.ranking != t2.ranking
}

fact repositoryCanBeForkedMultipleTimes {
	all fr: ForkedRepository | some s: Submission | fr = s.forkedRepository
}



fact userIsValid {
  // User email addresses must be unique
  all disj u1, u2: User | u1.email != u2.email
  // User first and last names cannot be empty
  all u: User | #u.firstName > 0 and #u.lastName > 0
}


fact tournamentPeriodValid {
  // The registration deadline must be before the starting date
  all t: Tournament | t.registrationDeadline.timeStamp < t.startingDate.timeStamp
}


fact teamSizeValid {
  // A team must have members between the min and max students per team of a battle
  all t: Team | 
    let b = t.battle | 
      #t.members >= b.minStudentsPerTeam and #t.members <= b.maxStudentsPerTeam
}


fact battleIsValid {
  // The submission deadline must be after the registration deadline
  all b: Battle | b.submissionDeadline.timeStamp > b.registrationDeadline.timeStamp
  // Each team in a battle must have a submission
  all b: Battle | all t: b.teams | some s: Submission | s.team = t
  // The number of teams must respect the min and max number of students per team
  all b: Battle | all t: b.teams | #t.members >= b.minStudentsPerTeam and #t.members <= b.maxStudentsPerTeam
}


fact repoBelongToOneCodeKata {
  // Each repository must be associated with exactly one code kata
  all r: Repository | one r.codeKata
}


fact codeKataValid{
  // A code kata must have at least one test case and one building script
  all ck: CodeKata | #ck.testCases > 0 and #ck.buildingScripts > 0
}


fact submissionValid {
  // A submission must be associated with a forked repository
  all s: Submission | one fr: ForkedRepository | s.forkedRepository = fr
}


// Assertions and checks would be expanded similarly to test the model
assert UniqueEmails {
  no disj u1, u2: User | u1.email = u2.email
}

// Assertion to ensure that no student is invited to the same tournament more than once
assert NoDuplicateInvitations {
  all t: Tournament, s: Student | lone i: Invitation | i.team.battle in t.battles and i.student = s
}

// Assertion to check that all teams in a battle have the correct number of members
assert CorrectTeamSizeForBattle {
  all b: Battle | all t: b.teams | 
    #t.members >= b.minStudentsPerTeam and #t.members <= b.maxStudentsPerTeam
}


// Assertion to ensure that each battle has an associated repository
assert EveryBattleHasRepository {
  all b: Battle | one b.repository
}

// Assertion to ensure that the starting date of a tournament is in the future (assuming DateTime is modeled correctly)
assert TournamentStartsInFuture {
  all t: Tournament | t.startingDate.timeStamp > DateTime.timeStamp
}

// Assertion that a student cannot be part of two teams in the same battle
assert StudentNotInMultipleTeamsPerBattle {
  all b: Battle | no disj t1, t2: b.teams | some s: Student | s in t1.members and s in t2.members
}

// Assertion to ensure that all repositories linked to a battle through a submission have the same code kata
assert ConsistentCodeKataInBattle {
  all b: Battle | let katas = b.teams.submissions.forkedRepository.codeKata | one katas
}

// Assertion to check that the ranking scores correspond to the students participating in the tournament
assert RankingScoresMatchTournamentParticipants {
  all r: Ranking | all s: r.scores | s.student in r.tournament.battles.teams.members
}

// Now, to check these assertions, you would use the check command in Alloy:
check UniqueEmails for 5
check NoDuplicateInvitations for 5
check CorrectTeamSizeForBattle for 5
check EveryBattleHasRepository for 5
check TournamentStartsInFuture for 5
check StudentNotInMultipleTeamsPerBattle for 5
check ConsistentCodeKataInBattle for 5
check RankingScoresMatchTournamentParticipants for 5




