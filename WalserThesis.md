The key idea is the importance of students' ability to read, understand, and trace code to be able to write programs successfully.  RUR-PLE provides a interactive environment which is well suited to testing and developing this ability.  The focus is to use this to support students' ability to use and understand iteration.  We can present the student with a program that uses iteration and an environment and see if they can predict the program's behavior.  They can input their prediction via the mouse and keyboard by interacting with the robot directly.  When they are done, they can watch the program execute to see if their prediction was correct or, if not, see where their prediction went wrong as well as possibly get some additional feedback.  From what I can tell, something like this has not yet been tried.  An open question is how much beyond showing the execution of the program and allowing the student to compare its behavior to their prediction to do.  Although it would probably be easier to diagnose errors in the student's thinking from this kind of interaction than a program writing task, the questions remains of how to diagnose these errors, what kind of feedback to give, and how to generate such feedback.  Longer-term idea is that students could also be asked to somehow identify the higher-level apparent purpose of what a given program is trying to accomplish.

To assess the learning gain after these interactions with RUR-PLE, an evaluation with student trials would be performed.  The student would be given a pretest before and a simple model of the student's knowledge would have to be created.  A post-test given afterward would allow for a comparison with the original model.  The test could consist of multiple-choice or short answer questions, (probably simpler) program tracing tasks, or simple program writing tasks (which would be assessed by whether they cause the appropriate changes to the state of the environment).  A control group would have to do some other task between the tests to give something to compare to and to factor out performance gain due to familiarity with the tests.  The exact make-up of the tests and the student model and how to build the latter from the former are open questions, as well as what should be done to familiarize the student with RUR-PLE before starting.

The simple student model could also be used to help choose the tracing tasks to give the student.  First of all, tasks could be chosen based on their level of difficulty.  Tasks that are too easy or too difficult for a particular student are not likely to help them learn.  Secondly, tasks could potentially also be chosen based on trying to address specific deficiencies the student demonstrated in the pretest.  The success of the student model and problem selection components in helping choose appropriate tracing tasks to maximize the student's learning gain could be measured by comparing against a second control group where tracing tasks are chosen randomly or in a fixed order.  How to assess appropriate difficulty level and what concepts to target, and how exactly to measure and compare learning gains are open questions.  Longer-term ideas include using data mining of logs of previous student interactions with the system and/or machine learning to adapt and improve the problem selection component over time.


---

Relevant papers:

[Further evidence of a relationship between explaining, tracing and writing skills in introductory programming](Lister09.md) -- Examines the importance of ability to trace and explain code, provides much of the inspiration for my idea, and the test questions may be useful

[Improving the mental models held by novice programmers using cognitive conflict and jeliot visualisations](Ma09.md) -- Jeliot tool is based on a similar idea and the paper contains a concept map, and concepts are associated with exercises (MdJ) which could be useful for tests, I guess you could say my idea promotes learning through cognitive conflict, and there may be some ideas for error feedback here

[The effect of visualizing roles of variables on student performance in an introductory programming course](AlBarakati09.md) -- Some comments on effective visualizations

[Estimating programming knowledge with Bayesian knowledge tracing](Kasurinen09.md) -- method of measuring student knowledge

Understanding student performance on an algorithm simulation task:  implications for guided learning -- talks about program tracing tasks

[Wu's castle- teaching arrays and loops in a game](Eagle08.md) -- another visual environment for helping teach iteration

[A taxonomy of task types in computing](Bower08.md) -- taxonomy of types of tasks students can be asked to perform, including prediction tasks

[The mystery of "b = (b == false)"](Reges08.md) -- direct evidence of importance of reading and understanding code

[Identifying important and difficult concepts in introductory computing courses using a delphi process](Goldman08.md) -- list of topics to include in assessments

[Factors in novice programmers' poor tracing skills](Vainio07.md) -- advocates benefits of practicing tracing tasks, and gives suggestions for making execution visualization effective

[Adaptive testing for hierarchical student models](Guzman07.md) -- sophisticated system for building a model of student knowledge and doing problem selection

[Results from the evaluation of the effectiveness of an online tutor on expression evaluation](Kumar05a.md) -- suggests that the more information the system provides about why the program is doing what it is doing when it is executing, the more effective this will be as a learning tool

[Generation of problems, answers, grade, and feedback---case study of a fully automated tutor](Kumar05b.md) -- advocates template-based generation (for automatic problem generation) for problems involving semantics of programs and says the more information a system provides about why a student's solution is incorrect, the more learning will take place

[A tutor for counter-controlled loop concepts and its evaluation](Dancik03.md) -- system very similar to my idea, but more basic, with only one loop type and prediction of number of iterations and console output supported; also evaluated in a very similar manner as my plan

[A Scalable Solution for Adaptive Problem Sequencing and its Evaluation](Kumar06.md) -- adaptive problem selection based on concepts addressed by problems and not mastered by students

[Predictive vs. passive animation learning tools](Taylor09.md) -- system based on similar idea to mine, used with graph algorithms problems