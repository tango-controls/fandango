What's New
==========

New in Fandango 11
------------------

news are that now you have all Tango types available as argin/argout types in commands (and images have been added to attributes).

 - The old syntax still works (DevVarStringArray for argin, anything you declare for argout); but with the new one you just type:

       SumSomeNumbers = DevDouble(sum(SPECTRUM(float,ARGS))) #Instead of sum(map(float,ARGS)) which is still available

 - The syntax for typed arguments now replaces ARGS by {SCALAR/SPECTRUM}({int/str/float/bool},ARGS)

 - And Voila!!, now DynamicCommands become functions in your attribute calls!!: SumAttr = SumSomeNumbers([Attr1,Attr2,Attr3])

Apart of that you have new keywords in Attributes/Commands/States:

 - SCALAR/SPECTRUM/IMAGE : for creating typed attributes   ( Attr=SPECTRUM(float,...) instead of Attr=DevVarDoubleArray(...)  ) ; the main advantage is that it allows compact syntax and having Images as DynamicAttributes.

 - @COPY:a/dev/name : It COPIES! your DynamicAttributes from another dynamic device (e.g., for all power supplies you just have one as template and all the rest pointing to the first one, update one and you update all).

 - @FILE:filename.txt : It reads the attributes/states/commands from a file instead of properties; for templating hundreds of devices w/out having to go one by one in Jive. 
