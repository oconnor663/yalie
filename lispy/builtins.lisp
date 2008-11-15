(set-locally true (quote true))
(set-locally false () )
(set-locally nil () )

(set-locally ls (fn (:r rest) rest))

(set-locally append (fn (:r rest)
  (if (= nil rest)
      ()
      (if (not (isls (car rest)))
	  (cons (car rest) (call append (cdr rest)))
          (if (= nil (car rest))
	      (call append (cdr rest))
	      (cons (car (car rest)) (call append (cons (cdr (car rest)) (cdr rest)))))))))

(set-locally map (fn (f args)
  (if (= args nil)
      nil
      (cons (call f (ls (car args))) (map f (cdr args))))))

(set-locally reverse (fn (list)
  (set-locally r-helper (fn (l1 l2)
			  (if (= l1 nil)
			      l2
			      (r-helper (cdr l1) (cons (car l1) l2)))))
  (r-helper list ())))
	  
(set-locally semiquote (form (x)
  (if (= x nil)
      nil
      (if (not (isls x))
      	  (ls (quote quote) x)
      	  (if (= (car x) (quote unquote))
	      (if (= (cdr x) nil)
	      	  (raise "Unquote needs an argument")
 		  (if (not (= (cdr (cdr x)) nil))
		      (raise "Too many args to unquote")
		      (car (cdr x))))
	      ((fn () (set-locally ret nil)  ## Why the hell is it this way?
	      	  (tag chop)
		  (if (= (car x) nil)
		      (set-locally ret (cons (ls (quote ls) nil) ret))
 		      (if (not (isls (car x)))
		      	  (set-locally ret (cons (ls (quote semiquote) (car x)) ret))
		      	  (if (= (car (car x)) (quote unquote-splice))
		      	      (if (= (cdr (car x)) nil)
			      	  (raise "Unquote-splice needs an argument")
			      	  (if (not (= (cdr (cdr (car x))) nil))
			      	      (raise "Too many args to unquote-splice")
			      	      (set-locally ret (cons (car (cdr (car x))) ret))))
		              (set-locally ret (cons (ls (quote ls) (ls (quote semiquote) (car x))) ret)))))
 		  (set-locally x (cdr x))
 		  (if (not (= x nil))
		      (goto chop)
		      nil)
 		  (ls (quote call) (quote append) (cons (quote ls) (reverse ret))))))))))


(set-locally tag (form (x) ()))

(set-locally deform (form (args :b body)
	     	      (if (not (isls args))
		       	  (raise "deform needs a form declaration")
			  `(set-locally ,(car args) (form ,(cdr args) ;body)))))

(deform (def args :b body)
  (if (isls args)
      `(set-locally ,(car args) (fn ,(cdr args) ;body))
      (if (not (= (cdr body) nil))
          (raise "Too many arguments to def")
          `(set-locally ,args ,(car body)))))

(deform (and :r rest)
  (if (= rest nil)
      `T	
      `(if ~,(car rest)
      	    F
 	    (and ;(cdr rest)))))

(deform (or :r rest)
  (if (= rest nil)
      `F	
      `(if ,(car rest)
      	   T
 	   (or ;(cdr rest)))))

(deform (while cond :b body)
  `(do (tag loop)
       ;body
       (if ,cond
	   (goto loop)
	   nil)))

(def (len list)
     (if ~(isls list)
       (raise "Not a list...")
       (if (= list ())
	   0
	   (+ 1 (len (cdr list))))))

(def (sum list)
     (if ~(isls list)
       (raise "Not a list...")
       (if (= list ())
	   0
	   (+ (car list) (sum (cdr list))))))

