library(RMySQL)
require(rfigshare)

cric_upload_image <- function(db_row) {
  print(
    paste0(
      "Processing ",
      db_row["nome"]
    )
  )
  
  id <- fs_create(
    paste0(
      "CRIC Cervix Microscope Slide Image #",
      db_row["id"]
    ),
    paste0(
      "Image ",
      db_row["id"],
      " Image ID from microscope slides of the uterine cervix ",
      "using the conventional smear (Pap smear). ",
      "Data visualisation of classification available at http://database.cric.com.br/classification/image/",
      db_row["id"],
      "."
    ),
    type = "figure"
  )

  fs_upload(
    id,
    paste0(
      "../searchable-image-database/backend/src/assets/imagens/base_interna/",
      db_row["nome"]
    )
  )

  fs_add_authors(
    id,
    c(
      "0000-0002-6002-857X",
      "0000-0002-9514-9312",
      "0000-0002-5440-5885"
    )
  )

  fs_add_categories(
    id,
    c(
      "Cancer",
      "Cell Biology",
      "Cell Development, Proliferation and Death",
      "Computational Biology",
      "Pathology",
      "Cancer Cell Biology",
      "Cancer Diagnosis"
    )
  )

  fs_add_tags(
    id,
    c(
      "cervical cancer",
      "pap smears",
      "quality monitoring",
      "imaging base",
      "cervical cell classification",
      "Bethesda system"
    )
  )
}

db <- dbConnect(
  MySQL(),
  user='root',
  password='123.456',
  dbname='cric',
  host='0.0.0.0'
)

query <- dbSendQuery(
  db,
  'SELECT * FROM imagem where id > 1'
)

data <- fetch(
  query,
  n=Inf
)

apply(
  data,
  1,
  cric_upload_image
)