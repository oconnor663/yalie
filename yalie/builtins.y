(def (eval x) x.eval)
(def (print x) x.print)
(def (do (rest rest))
     (if (rest.isa Nil) ()
	 (rest.cdr.isa Nil) rest.car
	 (car (while (not (rest.cdr.isa Nil))
		     (set rest (rest.cdr))))))

(def (ls (rest rest)) rest)
(def (car x) x.car)
(def (cdr x) x.cdr)
(def (setcar x y) (x.setcar y))
(def (setcdr x y) (x.setcdr y))
(def (len x)
     (if x
	 (1.+ (len (cdr x)))
	 0))
(def (append (rest rest))
     (if (rest.isa Nil) ()
	 (rest.cdr.isa Nil) rest.car
	 (rest.car.isa Nil) (call append rest.cdr)
	 (cons rest.car.car (call append rest.car.cdr rest.cdr))))

(def (< a b) (a.< b))
(def (= a b) (a.= b))
(def (<= a b) (or (< a b) (= a b)))
(def (> a b) (and (not < a b) (not = a b)))

(def (+ (rest rest))
     (if rest
	 ((car rest).+ (call + (cdr rest)))
	 0))
(def (* (rest rest))
     (if rest
	 ((car rest).* (call * (cdr rest)))
	 1))
(def (- x (rest rest))
     (if rest
     	 (+ x (* -1 (call + rest)))
	 (* -1 x)))
(def (/ a b) (a./ b))
(def (% a b) (a.% b))
