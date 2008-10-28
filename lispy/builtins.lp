(def (ls &rest rest)
    rest)

(def (append &rest rest)
    (if (not rest)
	()
	(if (= 1 (len rest))
	    (car rest)
	    (if (not (car rest))
		(call append (cdr rest))
		(cons (car (car rest)) (call append (cons (cdr (car rest)) (cdr rest))))))))

(def (len list)
    (if (not list)
	0
	(+ 1 (len (cdr list)))))

(def (map f list)
    (if (null list)
	()
	(cons (f (car list)) (map f (cdr list)))))

(deform (do &rest rest)
    (ls (append (ls (quote lambda) ()) rest)))

(deform (let &rest rest)
    (if (isls (car rest))
	(quote ((lambda (unquote (map car (car rest))) (unquote-splice (cdr rest)))
		(unquote-splice (map (lambda (x) (car (cdr x))) (car rest)))))
	(if (= 2 (len rest))
	    (quote (def (unquote (car rest)) (unquote (car (cdr rest)))))
	    (quote ((lambda ((unquote (car rest))) (unquote-splice (cdr (cdr rest))))
		    (unquote (car (cdr rest))))))))
	

(deform (for var &rest rest)
    (if (= (car rest) (quote in))))
  
    