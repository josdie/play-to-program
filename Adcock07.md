Which Pointer Errors Do Students Make?<br>
Adcock et al., Page 9<br>
SIGCSE'07<br>
<br>
An instrumentation technology that notifies students of pointer errors in C++ programs. -- RD<br>
<br>
DJW adds, they classified states for pointers and defined a state diagram and classified transitions as being safe, possibly dangerous, and always bad.  Their runtime technology reports when non-safe pointer state transitions are made.  It also logs all errors and centralizes collection of the log data.  In the paper they discuss not only their findings after analyzing the data (mainly about student behavior in regards to making different kinds of pointer errors), but also discuss ethical issues related to the collection of this data.