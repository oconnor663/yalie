(def (ls &rest rest)
     rest)

(def (append &rest rest)
     (if (not rest)
     	 ()
	 (if (= 1 (len rest))
	     (car rest)
	     (if (not (car rest))
	         (car (cdr rest))
		 (if (= 2 (len rest))
		     (cons (car (car rest)) (append (cdr (car rest)) (car (cdr rest))))
		     (append (car rest) (call append (cdr rest))))))))

(def (len list)
     (if (not list)
     	 0
	 (+ 1 (len (cdr list)))))

(deform (do &rest rest)
	(ls (append (ls (quote lambda) ()) rest)))