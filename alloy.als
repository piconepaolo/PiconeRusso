sig DateTime {}
sig File{}

abstract sig User {
	email: String,
	firstName: String,
	lastName: String
}

sig Educator extends User {
	tournamentCreated: some Tournament,
}

sig Student extends User {}

sig Team {
	member: some Student,
	repository: one ForkedRepository,
	submission: some Submission
}

sig CodeKata {
	description: String,
	test: some File,
	automationScript: some File
}

sig Submission {
	evaluation: lone Evaluation
}

sig Evaluation {
	points: Int
}

one sig Accepted {}
sig Invitation {
	link: String,
	expirationDate: one DateTime,
	accepted: lone Accepted,
	senderStudent: one Student,
	invitedStudent: one Student,
}

sig Ranking {
	competitor: some Student,
}

sig Tournament {
	registrationDeadline: one DateTime,
	startingDate: one DateTime,
	battle: some Battle,
	ranking: one Ranking
}

abstract sig Repository {
	link: String
}

sig OriginalRepository extends Repository {}
sig ForkedRepository extends Repository {}

one sig Closed {}
sig Battle {
	registrationDeadline: one DateTime,
	submissionDeadline: one DateTime,
	maxNumberOfStudentsPerTeam: Int,
	minNumberOfStudentsPerTeam: Int,
	team: some Team,
	repository: one OriginalRepository,
	codeKata: lone CodeKata,
	closed: lone Closed
}


sig Score {
	student: one Student,
	tournament: one Tournament
}


pred show [] {
	some Educator
}

run show for 5

fact pointsRange {
	all e: Evaluation | e.points >= 0 and e.points <= 100
}


fact invitationDifferentParties {
	all i: Invitation | i.senderStudent != i.invitedStudent
}

