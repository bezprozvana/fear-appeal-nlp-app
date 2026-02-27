# fear-appeal-nlp-app

Застосунок для автоматизованого виявлення апеляції до страху в текстових повідомленнях.  
Модель побудована на основі XLM-RoBERTa та інтегрована у графічний інтерфейс (Tkinter).

## Опис

Програма аналізує введений текст та визначає, чи містить він ознаки мовленнєвого прийому апеляції до страху.  
Результат відображається у вигляді класу та ймовірностей для обох категорій.

## Структура проєкту

- `src/` – вихідний код застосунку  
- `assets/ui_bg.png` – фон інтерфейсу  
- `models/xlm_roberta_fear/` – папка з навченою моделлю  
- `requirements.txt` – список залежностей  

## Датасет
Датасет збережено окремо (Google Drive): https://drive.google.com/drive/folders/1bALlj75dROiniMTVY-nzO3JMd5p9VwiC?usp=sharing
Структура папок у датасеті:
- `1/` – тексти з апеляцією до страху
- `0_clean/` – нейтральні тексти
- `0_other/` – інші негативні приклади

## Навчання моделі

Навчання виконувалося у Google Colab:  
https://colab.research.google.com/drive/1EvlyV3Kl9voT9HjlA_nOH6w_uPa46O_o?usp=sharing

Після навчання модель потрібно зберегти та розмістити у папці: models/xlm_roberta_fear/

## Встановлення

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

Запуск: python src/app.py
Якщо модель відсутня у папці models/xlm_roberta_fear, застосунок не зможе виконати прогнозування.
