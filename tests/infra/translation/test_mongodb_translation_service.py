import asyncio
from typing import Iterable

import pytest

from src.application.translation.service import TranslationService
from src.domain.translation.translation import Translation
from src.infra.provider.google.web.constants import Lang
from src.infra.provider.google.web.provider import GoogleWebTranslationProvider
from src.infra.repositories.translation.mongodb import MongoDBTranslationRepository


@pytest.fixture(scope="session")
def challenge_raw_translation_data() -> str:
    return r"""
)]}'

4047
[["wrb.fr","MkEWBc","[[\"ˈCHalənj\",null,\"en\",[[[0,[[[null,9]],[true]]]],9],[[\"challenge\",null,null,9]],null,[\"challenge\",\"auto\",\"ru\",true]],[[[null,\"ispytaniye\",null,null,null,[[\"испытание\",null,null,null,[[\"испытание\",[4],[]],[\"бросать вызов\",[4],[]],[\"вызов\",[2,5,11],[]]]]]]],\"ru\",1,\"en\",[\"challenge\",\"auto\",\"ru\",true]],\"en\",[\"challenge\",[[[\"noun\",[[\"a call to take part in a contest or competition, especially a duel.\",\"he accepted the challenge\",true,null,null,[[[[\"dare\"],[\"provocation\"],[\"summons\"]]]]],[\"an objection or query as to the truth of something, often with an implicit demand for proof.\",\"a challenge to the legality of the order\",true,null,null,[[[[\"confrontation with\"],[\"dispute with\"],[\"stand against\"],[\"test of\"],[\"opposition\"],[\"disagreement with\"],[\"questioning of\"],[\"defiance\"],[\"ultimatum\"]]]]],[\"exposure of the immune system to pathogenic organisms or antigens.\",\"recently vaccinated calves should be protected from challenge\",null,null,[[\"Medicine\"]]]],null,1],[\"verb\",[[\"invite (someone) to engage in a contest.\",\"he challenged one of my men to a duel\",true],[\"dispute the truth or validity of.\",\"employees challenged the company's requirement\",null,null,null,[[[[\"question\"],[\"disagree with\"],[\"object to\"],[\"take exception to\"],[\"confront\"],[\"dispute\"],[\"take issue with\"],[\"protest against\"],[\"call into question\"],[\"demur about/against\"],[\"dissent from\"],[\"be a dissenter from\"]]]]],[\"expose (the immune system) to pathogenic organisms or antigens.\",null,null,null,[[\"Medicine\"]]]],null,2]],6,true],[[[null,\"he needed something both to \\u003cb\\u003echallenge\\u003c/b\\u003e his skills and to regain his crown as the king of the thriller\"],[null,\"he accepted the \\u003cb\\u003echallenge\\u003c/b\\u003e\"],[null,\"a world title \\u003cb\\u003echallenge\\u003c/b\\u003e\"],[null,\"recently vaccinated calves should be protected from \\u003cb\\u003echallenge\\u003c/b\\u003e\"],[null,\"I heard the \\u003cb\\u003echallenge\\u003c/b\\u003e “Who goes there?”\"],[null,\"the ridge is a \\u003cb\\u003echallenge\\u003c/b\\u003e for experienced climbers\"],[null,\"a \\u003cb\\u003echallenge\\u003c/b\\u003e to the legality of the order\"]],6,7],null,null,[[[\"noun\",[[\"вызов\",null,[\"call\",\"challenge\",\"invocation\",\"summons\",\"defiance\",\"dare\"],1,true],[\"проблема\",null,[\"problem\",\"issue\",\"challenge\",\"question\",\"poser\",\"proposition\"],1,true],[\"сложная задача\",null,[\"challenge\",\"floorer\",\"egg-dance\"],2,true],[\"отвод\",null,[\"tap\",\"challenge\",\"diversion\",\"branch\",\"bend\",\"offset\"],3,true],[\"сомнение\",null,[\"doubt\",\"question\",\"challenge\",\"hesitation\",\"discredit\",\"query\"],3,true],[\"оклик\",null,[\"hail\",\"call\",\"challenge\",\"holla\",\"hollo\",\"holloa\"],3,true],[\"вызов на дуэль\",null,[\"challenge\"],3,true],[\"опознавательные сигналы\",null,[\"challenge\"],3,true]],\"ru\",\"en\"],[\"verb\",[[\"оспаривать\",null,[\"challenge\",\"dispute\",\"contest\",\"contend\",\"debate\",\"litigate\"],1,true],[\"бросать вызов\",null,[\"challenge\",\"defy\",\"affront\",\"outdare\",\"bid defiance to\"],2,true],[\"подвергать сомнению\",null,[\"question\",\"challenge\",\"query\",\"dispute\",\"reflect on\",\"reflect upon\"],3,true],[\"вызывать\",null,[\"call\",\"cause\",\"induce\",\"call forth\",\"summon\",\"challenge\"],3,true],[\"требовать\",null,[\"require\",\"demand\",\"claim\",\"ask\",\"take\",\"challenge\"],3],[\"окликать\",null,[\"hail\",\"holler\",\"call\",\"challenge\",\"speak\",\"hallo\"],3],[\"спрашивать пропуск\",null,[\"challenge\"],3],[\"спрашивать пароль\",null,[\"challenge\"],3],[\"сомневаться\",null,[\"doubt\",\"question\",\"distrust\",\"challenge\",\"disbelieve\",\"mistrust\"],3],[\"отрицать\",null,[\"deny\",\"negate\",\"disavow\",\"gainsay\",\"disown\",\"challenge\"],3],[\"давать отвод присяжным\",null,[\"challenge\"],3]],\"ru\",\"en\"]],19,true],\"ˈCHalənj\",null,\"en\",1]]",null,null,null,"generic"]]
54
[["di",27],["af.httprm",26,"-494604635527266197",6]]
26
[["e",4,null,null,4399]]
    """


@pytest.fixture(scope="session")
def chance_raw_translation_data() -> str:
    return r"""
")]}'

104
[["wrb.fr","MkEWBc",null,null,null,[13],"generic"],["di",32],["af.httprm",32,"7098306939635456246",5]]
25
[["e",4,null,null,140]]
"
    """


@pytest.fixture(scope="function")
def path_google_wep_translation_provider(
    challenge_raw_translation_data: str, mocker
):
    mocker.patch(
        "src.infra.provider.google.web.translator.Translator._call_translate",
        return_value=(challenge_raw_translation_data, None)
    )


@pytest.mark.asyncio
async def test_mongodb_google_translation_service(
        path_google_wep_translation_provider,
        mongodb_google_translation_service: TranslationService,
        mongodb_translation_repo: MongoDBTranslationRepository,
        google_translation_provider: GoogleWebTranslationProvider
):
    word = "challenge"
    translation: "Translation" = await mongodb_google_translation_service.translate(
        word=word, dst_lang=Lang.RU
    )
    assert translation and translation.word == word

    translations: Iterable["Translation"] = await mongodb_translation_repo.find(word=word)
    assert [item.word for item in translations] == [word]
