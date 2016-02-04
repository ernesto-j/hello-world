# hello-world
An exercise in github and markdown

#Header1
##Header2
###Sub-Header3

This is **bold**
Here are some *italics*
***
#New paragraph
Numbered list
1. item 1
2. item 2

Bulleted list
* item 1 __with bold__
* item 2 _italics_

A link to [google](www.google.com)

An equation:
$ E = mc^{2} $

Code inline:
'r Sys.Date() '

```{r}
#some code
```
#Some git commands
*git diff 939d..235f6 >what has changed?
*git checkout 0145d >rollback
*git rebase ...go back in time as if never happened

*git bisect >pick point between good and bad 
*commit - figure out which one was first bad

#Some useful markdown tricks in with Rmarkdown
*Remove program text in reports
```{r echo = FALSE}
```
```{r eval=FALSE, fig.width=3, fig.height=5 ,warnings =FALSE, engine = python, message = false}
```
*Set up parameters 
---
output: html_document
params:
	symbol: AMZN
---

e.g getdata(params$symbol

#` param$symbol`

