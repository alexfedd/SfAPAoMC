import warnings

import pandas as pd
from icecream import ic
from sklearn.metrics.pairwise import cosine_similarity
import torch
from transformers import AutoModel, AutoTokenizer

class CategoryConfig:
    """
        Configurator for the classifier.
        Contains settings for tokenizer, models and description of industries.
    """
    tokenizer = AutoTokenizer.from_pretrained('sberbank-ai/sbert_large_nlu_ru')
    model = AutoModel.from_pretrained('sberbank-ai/sbert_large_nlu_ru')
    industries_description = {
        'Сельское хозяйство и пищевая промышленность': 'Сельское хозяйство, пищевая промышленность, фермерство, '
                                                       'производство продуктов питания, агробизнес, земледелие, '
                                                       'животноводство, молочные продукты, мясо, зерновые культуры, '
                                                       'овощи, фрукты, рыболовство, переработка продуктов, '
                                                       'сельскохозяйственная техника, фермерские рынки, органическая '
                                                       'продукция',
        'Добывающая промышленность': 'Добыча полезных ископаемых, уголь, нефть, газ, металлы, горнодобывающая '
                                     'промышленность, карьерные работы, бурение, разведка месторождений, рудники, '
                                     'добыча золота, добыча серебра, полезные ископаемые, шахты, нефтяные вышки, '
                                     'газовые месторождения',
        'Обрабатывающая промышленность': 'Производство товаров, переработка сырья, фабрики, заводы, машиностроение, '
                                         'металлообработка, текстильная промышленность, производство автомобилей, '
                                         'производство электроники, химическая промышленность, деревообработка, '
                                         'производство пластмасс, мебельная промышленность, упаковочные материалы, '
                                         'производственные линии',
        'Энергетика': 'Электроэнергетика, газовая промышленность, нефть, возобновляемые источники энергии, '
                      'атомная энергетика, солнечная энергетика, ветровая энергетика, гидроэнергетика, энергетические '
                      'компании, электростанции, распределение электроэнергии, энергосети, энергетическая '
                      'эффективность, топливные элементы, энергогенерация',
        'Строительство и недвижимость': 'Строительство зданий, инфраструктуры, управление недвижимостью, девелопмент, '
                                        'жилое строительство, коммерческая недвижимость, архитектура, строительные '
                                        'компании, подрядчики, строительные материалы, инженерные сети, '
                                        'жилищное строительство, офисные здания, торговые центры, строительные '
                                        'проекты, проектирование, строительные работы',
        'Транспорт и логистика': 'Грузовые перевозки, пассажирские перевозки, управление цепями поставок, '
                                 'логистические услуги, транспортные компании, авиаперевозки, морские перевозки, '
                                 'железнодорожные перевозки, автомобильные перевозки, складские услуги, '
                                 'экспедирование грузов, транспортная логистика, логистические центры, дистрибуция, '
                                 'доставка, транспортные средства',
        'Информационные технологии и телекоммуникации': 'Разработка программного обеспечения, интернет-услуги, '
                                                        'телекоммуникационные услуги, IT-консалтинг, компьютерные '
                                                        'технологии, программирование, IT-компании, разработка '
                                                        'веб-сайтов, сетевые технологии, кибербезопасность, '
                                                        'мобильные приложения, базы данных, облачные вычисления, '
                                                        'IT-инфраструктура, телекоммуникационные сети, '
                                                        'интернет-провайдеры, электронная коммерция',
        'Финансовые услуги': 'Банковские услуги, страхование, инвестиции, управление активами, финансовые компании, '
                             'кредитование, брокерские услуги, финансовый консалтинг, бухгалтерский учет, '
                             'фондовый рынок, банковские операции, финансовые институты, сберегательные счета, '
                             'страховые полисы, инвестиционные фонды, управление рисками, финансовое планирование',
        'Здравоохранение и социальные услуги': 'Медицинские услуги, больницы, социальные службы, фармацевтика, '
                                               'здравоохранение, клиники, медицинские исследования, медицинское '
                                               'оборудование, медицинская техника, врачи, медсестры, социальное '
                                               'обеспечение, уход за престарелыми, психическое здоровье, '
                                               'реабилитационные центры, аптеки, медицинское страхование, '
                                               'лабораторные исследования',
        'Образование и наука': 'Школы, университеты, исследовательские институты, образовательные программы, '
                               'высшее образование, начальное образование, среднее образование, дистанционное '
                               'обучение, научные исследования, учебные заведения, преподавание, академическая '
                               'деятельность, научные публикации, образовательные технологии, студенческое обучение, '
                               'научные конференции',
        'Туризм и гостиничный бизнес': 'Отели, туристические агентства, туроператоры, развлекательные мероприятия, '
                                       'туризм, путешествия, гостиницы, гостевые дома, курорты, экскурсии, отдых, '
                                       'путешествия, авиабилеты, бронирование отелей, туристические услуги, '
                                       'туристические достопримечательности, турпакеты, глэмпинг, отдых на природе, '
                                       'путешествия по миру',
        'Розничная торговля': 'Магазины, супермаркеты, интернет-магазины, розничные сети, торговля, товары народного '
                              'потребления, продуктовые магазины, одежда, обувь, электроника, бытовая техника, '
                              'торговые центры, маркетинг, продажи, розничные операции, покупатели, клиентское '
                              'обслуживание, скидки, акции, торговля через интернет',
        'Медиа и развлечения': 'Телевидение, радио, кино, музыка, издательская деятельность, медиа-компании, '
                               'развлекательные мероприятия, шоу-бизнес, видеоигры, мультимедиа, социальные сети, '
                               'реклама, кинематограф, радиовещание, музыкальная индустрия, телешоу, телевидение в '
                               'прямом эфире, театры, концерты, издательства, журналы, газеты',
        'Юридические и профессиональные услуги': 'Юридические фирмы, консалтинг, аудит, бухгалтерия, правовые услуги, '
                                                 'адвокаты, юристы, юридическое консультирование, нотариусы, '
                                                 'юридические консультации, судебные разбирательства, '
                                                 'правовые документы, налоговое консультирование, аудиторские услуги, '
                                                 'бухгалтерский учет, профессиональные услуги, бизнес-консалтинг, '
                                                 'правовая защита, юридическое представительство'
    }


class CategoryDetector:
    """
    Classifier of categories of organizations by their OKVED description.

    Methods:
    - __init__: Initialize tokenizer, model and category embeddings.
    - _get_embedding: Retrieve embedding for a given text.
    - _classify_organization: Classifying organization based on similarity to category embeddings.
    - __call__: Applying a classifier to a DataFrame with organization data.


    Example Usage:
    import pandas as pd
    from org_category import category_detector

    if __name__ == "__main__":
        df = pd.read_csv(path_to_df)
        classified_df = category_detector(df)
        print(classified_df)
    """

    def __init__(self):
        self.tokenizer = CategoryConfig.tokenizer
        self.model = CategoryConfig.model
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        ic(self.device)
        self.model.to(self.device)
        self.category_embeddings = {category: self._get_embedding(description)
                                    for category, description in CategoryConfig.industries_description.items()}

    def _get_embedding(self, text: str) -> torch.Tensor:
        """
        Gets the embedding for the given text.

        :parameter
        text (str): Input text.

        :return
        torch.Tensor: Embedding of text.
        """
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=256).to(
            self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()

    def _classify_organization(self, text: str) -> str:
        """
        Classifies an organization based on similarity to embedding categories.

        Parameters:
        text (str): Description of the organization.

        Returns:
        str: The name of the most appropriate category.
        """
        embedding = self._get_embedding(text)
        similarities = {category: cosine_similarity([embedding], [category_embedding])[0][0]
                        for category, category_embedding in self.category_embeddings.items()}
        return max(similarities, key=similarities.get)

    def __call__(self, df: pd.DataFrame,
                 okvd_column_name: str = 'ОКВЭД2 расшифровка',
                 new_column_name: str = 'category',
                 fillna_name: str = 'Нет категории') -> pd.DataFrame:
        """
        Applies a classifier to a DataFrame with organization data.

        Parameters:
        df (pd.DataFrame): DataFrame with organizations data.
        okvd_column_name (str): The name of the column with the OKVED description.
        new_column_name (str): The name of the new column for the classification results.
        fillna_name (str): The name of the category applied to pd.Nan.

        Returns:
        pd.DataFrame: The updated DataFrame with the classification results.
        """
        df[okvd_column_name] = df[okvd_column_name].fillna(fillna_name)
        df[okvd_column_name] = df[okvd_column_name].astype(str)
        df[new_column_name] = df[okvd_column_name].apply(
            lambda x: fillna_name if x == fillna_name else self._classify_organization(x)
        )
        return df
