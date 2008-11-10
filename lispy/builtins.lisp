(set-locally True (quote True))
(set-locally False () )
(set-locally nil () )

(set-locally ls (fn (:r rest) rest))

(set-locally map (fn (f args)
  (put "here")
  (put args)
  (put (car args))
  (if (= args nil)
      nil
      (cons (call f (ls (car args))) (map f (cdr args))))))

(set-locally semiquote (form (x)
  (if (not (isls x))
      (ls (quote quote) x)
      (if (= (car x) (quote unquote))
	  (if (= (cdr x) nil)
	      (raise "Unquote needs an argument")
	      (if (not (= (cdr (cdr x)) nil))
		  (raise "Too many args to unquote")
		  (car (cdr x))))
	  (cons (quote ls) (map (fn (y) (ls (quote semiquote) y)) x))))))
      

(set-locally tag (form (x) ()))

(set-locally do (form (:b body) (ls (cons (quote fn) (cons () body)))))
