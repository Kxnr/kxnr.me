;;; layout.scm — shared layout and content helpers

(define nav-entries
  '(("About Me" . "about_me.html")
    ("Github"   . "https://github.com/Kxnr")))

(define (nav-links)
  (apply string-append
    (map (lambda (e) (ml->string `(li ,(ml-link (cdr e) (car e)))))
         nav-entries)))

; Background-clip text effect used in the hero banner.
; extra-classes are appended to the base class string.
(define (knockout text . extra-classes)
  (ml->string
    `(div class: ,(apply string-append
                         "border-inherit bg-background bg-clip-text text-transparent"
                         (map (lambda (c) (string-append " " c)) extra-classes))
          ,text)))

; Content section with a heading. Pass body content as a #[ ]# template literal.
(define (section title content)
  (ml->string
    `(div class: "p-4 border-t border-inherit first:border-none"
          (h2 class: "text-4xl w-full border-inherit text-bone mb-2" ,title)
          ,content)))

; Bulleted vertical list.
(define (vertical-list . items)
  (ml->string
    `(ul class: "list-disc list-inside"
         ,@(map (lambda (item) `(li ,item)) items))))

; Inline horizontal list with a separator between items.
(define (horizontal-list separator . items)
  (ml->string
    `(div (ul class: "inline list-none"
              ,@(map (lambda (item)
                       `(li class: ,(string-append "inline after:content-['" separator "'] last:after:content-none")
                            ,item))
                     items)))))

; Full page layout with hero banner — call page-open at top, page-close at bottom.
(define (page-open page-title)
  #[<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noai, noimageai">
  <title>#=(ml->string page-title)</title>
  <link rel="stylesheet" type="text/css" media="all" href="/css/output.css">
</head>
<body class="bg-charcoal text-bone border-bone z-0 h-dvh text-md">
  <div class="border-inherit flex items-center justify-center text-center bg-background p-4 border-b min-h-aspect">
    <div class="bg-charcoal border-inherit border-2 shadow-sm max-w-4xl grow p-4">
      #=(knockout "Connor Keane" "text-6xl")
      #=(knockout "Developer | Tinkerer | Science Enthusiast" "text-xl")
    </div>
  </div>
  <div class="border-inherit sticky top-0 w-full bg-copper shadow-sm content-center items-center border-b z-10 text-l">
    <div class="relative flex px-4 py-2 items-center">
      <div class="flex-none"><a href="/">KXNR</a></div>
      <ol class="flex space-x-8 ml-auto">
        #=(nav-links)
      </ol>
    </div>
  </div>
  <div class="bg-charcoal relative w-full z-0">
    <div class="container mx-auto p-2 md:p-4">
      <div class="border-inherit md:shadow-2xl md:p-2">
        <div class="bg-background-fade m-2">
          <div class="bg-charcoal bg-clip-padding p-2 border-4 border-transparent border-solid">
]#)

(define (page-close)
  #[          </div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
]#)

; Article layout — nav only, no hero banner, includes footer.
(define (article-open article-title)
  #[<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noai, noimageai">
  <title>#=(ml->string article-title) — Connor Keane</title>
  <link rel="stylesheet" type="text/css" media="all" href="/css/output.css">
</head>
<body class="bg-charcoal text-bone border-bone z-0 h-dvh text-md">
  <div class="sticky top-0 w-full bg-copper shadow-sm content-center items-center border-b z-10 text-l">
    <div class="relative flex px-4 py-2 items-center">
      <div class="flex-none"><a href="/">KXNR</a></div>
      <ol class="flex space-x-8 ml-auto">
        #=(nav-links)
      </ol>
    </div>
  </div>
  <div class="container mx-auto shadow-2xl p-4 m-4">
    <div class="border-inherit md:shadow-2xl md:p-2">
      <div class="bg-background-fade m-2">
        <div class="bg-charcoal bg-clip-padding p-2 border-4 border-transparent border-solid">
]#)

(define (article-close)
  #[        </div>
      </div>
    </div>
  </div>
  <footer>
    <p>&#169; 2024 Connor Keane.</p>
    <p>I don't use AI in my work, so don't use my work for your AI. Fair?</p>
  </footer>
</body>
</html>
]#)
