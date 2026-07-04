# Data

Raw CSVs are not committed to this repo (Kaggle's terms discourage redistribution, and they're 120MB+).

To fetch them yourself:

```bash
pip install kaggle
# place your Kaggle API token at ~/.kaggle/kaggle.json
kaggle datasets download -d olistbr/brazilian-ecommerce
unzip brazilian-ecommerce.zip -d data/
rm brazilian-ecommerce.zip
```

Then build the SQLite database:

```bash
python3 load_db.py
```

Source: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (CC BY-NC-SA 4.0)
