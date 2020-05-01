# DOI Generator for CRIC Searchable Image Database

We use [figshare](https://figshare.com/) as DOI provider.

## File Upload

To upload the files,
we provide `upload.R`
that uses [rfigshare](https://github.com/ropensci/rfigshare).
Use

```
$ Rscript upload.R
```

to execute the script.

## Save DOI

[rfigshare](https://github.com/ropensci/rfigshare)
doesn't have a function to edit funding information
and this requires a "manual" step.
Because of this,
`upload.R` doesn't make the images public
and doesn't get the DOI.

To pull the DOI
and
update the database,
we use `pull.py`.

``
$ python pull.py --token YOUR_FIGSHARE_API_TOKEN
```