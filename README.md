# hello-world
An exercise in github and markdown

## ScreenFixed valuation (branch: claude/screenfixed-valuation-88ic3d)

Pressure-tested Monte Carlo valuation of the ScreenFixed screen-repair business
(Brisbane CBD):

- **[VALUATION.md](VALUATION.md)** — written summary: revenue/SDE/valuation distributions,
  verified sale comps, rent reality check, sensitivity ranking, cited-vs-guessed flags
- **[whatif.html](whatif.html)** — interactive what-if tool (open in any browser, no install):
  live 10k-run Monte Carlo, sliders for every driver, tornado chart, JSON export
- **[model/params.yaml](model/params.yaml)** — all model inputs with source annotations;
  edit and re-run with real figures
- **[model/simulate.py](model/simulate.py)** — the offline model (`python3 model/simulate.py`,
  needs numpy/matplotlib/pyyaml); writes charts + `results.json` to `model/outputs/`

#Header1
##Header2
###Sub-Header3

This is **bold**
Here are some *italics*
***

Numbered list
1 item 1
2 item 2

Bulleted list
* item 1 __with bold__
* item 2 _italics_

A link to [google](www.google.com)

An equation:
$$ E = mc^{2} $$

Code inline:
'r Sys.Date() '

Code 
```{r}
#some code
```
#Some git commands
*git diff 939d..235f6 -what has changed?
*git checkout 0145d -rollback
*git rebase ...go back in time as if never happened
*git bisect -pick point between good and bad 
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

