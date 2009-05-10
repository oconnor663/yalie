### Anonymous function and form constructs ###
(deform (fn args (rest body))
 `(let ()
   (def (anon ;args)
    ;body)))

(deform (form args (rest body))
 `(let ()
   (deform (anon ;args)
    ;body)))

### Various useful operators ###
(def (eval x) x.eval)
(def (print x) x.print)
(def (eq a b) (a.eq b))
(def (is a b) (a.is b))

(def (do (rest rest))
     (if (rest.isa Nil) ()
	 (rest.cdr.isa Nil) rest.car
	 (car (while (not (rest.cdr.isa Nil))
		     (set rest (rest.cdr))))))

### List operators ###
(def (ls (rest rest)) rest)
(def (car x) x.car)
(def (cdr x) x.cdr)
(def (setcar x y) (x.setcar y))
(def (setcdr x y) (x.setcdr y))

(def (len x)
     (if x
	 (1.+ (len (cdr x)))
	 0))

(def (reverse list)
     (def (helper list rest)
	  (if list 
	      (helper (cdr list)
	      	      (cons (car list) rest))
	      rest))
     (helper list ()))

(def (append (rest rest))
     (if (rest.isa Nil) ()
	 (rest.cdr.isa Nil) rest.car
	 (rest.car.isa Nil) (call append
	 	       	    	  rest.cdr)
	 (cons rest.car.car
	       (call append rest.car.cdr
	       	     	    rest.cdr))))

(def (map fn (rest arg-lists))
     (def (map-single fn list)
	  (if list
	      (cons (fn (car list))
	      	    (map-single fn
		    		(cdr list)))))
     (if (not arg-lists)
	 (error))
     (if (car arg-lists)
	 (let (args (map-single car
				arg-lists)
	       rests (map-single cdr
				 arg-lists))
	   (cons (call fn args)
		 (call map fn rests)))))

(def (filter fn list)
     (if list
	 (if (fn (car list))
	     (cons (car list)
	     	   (filter fn (cdr list)))
	     (filter fn (cdr list)))))

(def (in obj list)
  (if (not list)         0
      (= obj (car list)) 1
      (in obj (cdr list))))
     
### Arithmetic operators ###
(def (= a b) (a.= b))
(def (< a b) (a.< b))
(def (<= a b) (or (< a b) (= a b)))
(def (> a b) (and (not < a b) (not = a b)))
(def (>= a b) (or (> a b) (= a b)))

(def (+ (rest rest))
     (if rest
	 ((car rest).+ (call + (cdr rest)))
	 0))

(def (* (rest rest))
     (if rest
	 ((car rest).* (call * (cdr rest)))
	 1))

(def (- x (rest rest))
     (if (not rest)
     	 (* -1 x)
	 (x.- (call + rest))))

(def (/ a b) (a./ b))
(def (% a b) (a.% b))
