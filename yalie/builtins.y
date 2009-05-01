# Evaluates body in the calling scope
(let do Form.child)
(do.def call ((rest args))
	(while args
	       (set args (args.cdr))))
