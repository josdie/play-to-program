# Playing to Program research project #
### Developing an Intelligent Tutoring System for introductory Computer Science ###

We are building an Intelligent Tutoring System (ITS) based on the RUR-PLE visual programming environment for Python.  It has the ability to automatically load problems within the environment, allows the user to input their solution, and then it can automatically assess their solution and provide feedback.  It can also adapt its behavior based on its interactions with the user.  This [system](Documentation.md) is being developed as part a research project within the MAPLE lab at the University of Maryland, Baltimore County's Department of Computer Science and Electrical Engineering.  The project is called the Playing to Program project and has [involved](People.md) both graduate and undergraduate researchers.  There are four main avenues for the [research](Papers.md) behind this system:

(1) [Student model](UndergradResearchProj1.md).  We have developed a simple recency-weighted performance-based model.  We are working on a more sophisticated Bayesian model.

(2) [Adaptive problem selection](WalserThesis.md).  We have developed a problem selection algorithm that chooses problems targeting concepts that the user has not demonstrated mastery of and problems that are at an appropriate level of difficulty.

(3) Automated diagnosis.  Our system can automatically check solutions to program prediction problems.  Future plans include more sophisticated diagnosis as well as the ability to assess solutions to program writing problems.

(4) RUR-PLE problem sets.  We have developed a set of program prediction (based on given code) and program writing (based on a given task) [problem templates](http://play-to-program.googlecode.com/files/rurprogs.pdf) involving the concept of iteration.  Future work could include more problem types as well as problems involving different concepts relevant to an introductory Computer Science course.

Abstracts of papers that we have written based on our work are below.

---

### Playing to Program: Towards an Intelligent Programming Tutor for RUR-PLE ###
#### Marie desJardins, Amy Ciavolino, Robert Deloatch, and Eliana Feasley ####
##### April 2011 #####

Intelligent tutoring systems (ITSs) provide students with a one-on-one tutor, allowing them to work at their own pace, and helping them to focus on their weaker areas. The RUR–Python Learning Environment (RUR-PLE), a game-like virtual environment to help students learn to program, provides an interface for students to write their own Python code and visualize the code execution (Roberge 2005). RUR-PLE provides a ﬁxed sequence of learning lessons for students to explore. We are extending RUR-PLE to develop the Playing to Program (PtP) ITS, which consists of three components: (1) a Bayesian student model that tracks student competence, (2) a diagnosis module that provides tailored feedback to students, and (3) a problem selection module that guides the student’s learning process. In this paper, we summarize RUR-PLE and the PtP design, and describe an ongoing user study to evaluate the predictive accuracy of our student modeling approach.

---

### Problem Selection of Program Tracing Tasks in an Intelligent Tutoring System and Visual Programming Environment ###
#### David Walser ####
##### April 2011 #####

Intelligent tutoring systems (ITSs) have been shown to be an effective supplementary teaching tool or aid for many domains.  Applying ITSs in open-ended domains such as computer programming is especially challenging, most notably when trying to assist with the process of programming itself.  Existing ITSs for programming focus on a very limited set of problems and concepts and are only useful early in an introductory CS course and a few limited places afterward.  Visual programming environments are another tool that have been used in introductory CS courses to help students learn basic concepts.  The key idea behind my work is the recognition of the importance of students' ability to read, understand, and trace code in order to write programs successfully.  A broader goal of my work is to show that an ITS based on a visual programming environment can be used to support students throughout an entire introductory CS course, without being severely constrained and limited to a small number of concepts and to low-level, simple tasks.  In my system, called RUR-ITS, students are given a program and are asked to predict the robot's behavior when running this program in a given environment.  RUR-ITS allows each problem to be assigned a difficulty level and multiple concepts that it involves within the conceptual model.  RUR-ITS can then use a problem selection algorithm to choose a problem that is most able to help the student master the concepts that they have not yet mastered.

---

RUR-PLE: http://code.google.com/p/rur-ple/