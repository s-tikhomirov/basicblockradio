ББ-153: Bitcoin Conference 2022. Часть 2: лайтнинг и сайдчейны

<div class="DraftEditor-paragraphElement" data-block="true" data-editor="9qaro" data-offset-key="9f6lf-0-0">
<div class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="9f6lf-0-0"><span data-offset-key="9f6lf-0-0">Продолжаем обзор идей и трендов в развитии биткоин-экосистемы по следам Bitcoin Conference в Майами. В этом выпуске говорим о протоколах поверх биткоина: с какими проблемами сталкиваются разработчики лайтнинг-кошельков, как развиваются децентрализованные биржи, и какие существуют подходы к дизайну сайдчейнов.</span></div>
</div>


<div class="DraftEditor-paragraphElement" data-block="true" data-editor="9qaro" data-offset-key="56oet-0-0">
<div class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="56oet-0-0"><span data-offset-key="56oet-0-0">Таймкоды:</span></div>

</div>
<ul>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="9ah70-0-0"><span data-offset-key="9ah70-0-0">02:45 повлияла ли на конференцию война в Украине?</span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="54gsf-0-0"><span data-offset-key="54gsf-0-0">08:35 тема регулирования криптовалют</span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="93gr-0-0"><span data-offset-key="93gr-0-0">09:45 выступление Питера Тиля о финансовой геронтократии</span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="463g8-0-0"><span data-offset-key="463g8-0-0">12:25</span> <a class="sc-1bctqj2-0 qOIqX" href="https://andrecronje.medium.com/the-rise-and-fall-of-crypto-culture-3d0e6fd3e0e9"> <span data-offset-key="463g8-1-0">эмоциональная статья Андре Кронье в защиту регулирования</span></a><span data-offset-key="463g8-2-0"> </span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="4tice-0-0"><span data-offset-key="4tice-0-0">15:55 обсуждали ли биткоин в контексте всей крипто-индустрии?</span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="648sa-0-0"><span data-offset-key="648sa-0-0">19:35 спасибо организаторам (лучше поздно, чем никогда)</span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="fc6bv-0-0"><span data-offset-key="fc6bv-0-0">23:05 сколько потратили на конференцию</span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="1ac75-0-0"><span data-offset-key="1ac75-0-0">23:45 переходим к главной теме: приложения на базе биткоина</span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="4feg9-0-0"><span data-offset-key="4feg9-0-0">25:05 насколько экономически целесообразен лайтнинг?</span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="arrrr-0-0"><span data-offset-key="arrrr-0-0">28:45 сравнение роста лайтнинга с DeFi</span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="ma2p-0-0"><span data-offset-key="ma2p-0-0">30:15 компании будут держать лайтнинг-узлы без прямой прибыли?</span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="7dqqd-0-0"><span data-offset-key="7dqqd-0-0">33:15 разница между узлами биткоина и лайтнинга</span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="7rkc6-0-0"><span data-offset-key="7rkc6-0-0">36:45 проблема ликвидности для лайтнинг-кошельков</span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="c716-0-0"><span data-offset-key="c716-0-0">42:35 вопросы приватности в лайтнинге</span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="174v2-0-0"><span data-offset-key="174v2-0-0">46:05 проблема интерактивности лайтнинга: почему телефон не может сам принять платёж?</span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="8hu17-0-0"><span data-offset-key="8hu17-0-0">48:35 как отделить протокол лайтнинга от хранения ключей? Проект Greenlight</span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="6osm5-0-0"><span data-offset-key="6osm5-0-0">50:20 дискуссии о спецификациях лайтнинга</span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="fsmce-0-0"><span data-offset-key="fsmce-0-0">56:35 разные подходы к стандарту инвойсов</span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="av78s-0-0"><span data-offset-key="av78s-0-0">1:01:05 протокол Taro &#8212; выпуск активов поверх лайтнинга</span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="22ano-0-0"><span data-offset-key="22ano-0-0">1:05:35 биткоин-протоколы помимо лайтнинга: covenants, они же заветы 🙂 а также CheckTemplateVerify и AnyPrevOut / NoInput</span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="beoii-0-0"><span data-offset-key="beoii-0-0">1:16:05 приходят ли новые люди в биткоин-разработку?</span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="eir3u-0-0"><span data-offset-key="eir3u-0-0">1:18:20 децентрализованные биржи в мире биткоина и дилемма KYC на уровне протоколов</span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="12fme-0-0"><span data-offset-key="12fme-0-0">1:29:15 контракты с оракулами (DLC)</span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="b5dck-0-0"><span data-offset-key="b5dck-0-0">1:35:35 возможности и риски взаимосвязей в финансовой системе</span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="b0q6k-0-0"><span data-offset-key="b0q6k-0-0">1:39:10 дискуссии вокруг сайдчейнов: Liquid vs RSK vs Thorchain</span></li>
</ul>
<p>Ссылки:</p>
<ul>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="324hh-0-0"><a class="sc-1bctqj2-0 qOIqX" href="https://andrecronje.medium.com/the-rise-and-fall-of-crypto-culture-3d0e6fd3e0e9"> <span data-offset-key="324hh-0-0">Andre Cronje &#8212; The rise and fall of crypto culture</span></a><span data-offset-key="324hh-1-0"> </span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="a88cr-0-0"><a class="sc-1bctqj2-0 qOIqX" href="https://drive.google.com/file/d/1Atcrrg7nO0eJotyNCA-ZDf69EyoJADkq/view"> <span data-offset-key="a88cr-0-0">The State of Lightning</span></a><span data-offset-key="a88cr-1-0"> </span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="9huhq-0-0"><a class="sc-1bctqj2-0 qOIqX" href="https://learning.chaincode.com/"><span data-offset-key="9huhq-0-0">Chaincode Seminars</span></a><span data-offset-key="9huhq-1-0"> </span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="7e45e-0-0"><a class="sc-1bctqj2-0 qOIqX" href="https://blog.blockstream.com/en-greenlight-by-blockstream-lightning-made-easy/"> <span data-offset-key="7e45e-0-0">Greenlight by Blockstream: Lightning Made Easy</span></a><span data-offset-key="7e45e-1-0"> </span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="bbc14-0-0"><a class="sc-1bctqj2-0 qOIqX" href="https://lightning.engineering/posts/2022-4-5-taro-launch/"><span data-offset-key="bbc14-0-0"> Announcing Taro: A New Protocol for Multi-Asset Bitcoin and Lightning</span></a><span data-offset-key="bbc14-1-0"> </span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="ducte-0-0"><a class="sc-1bctqj2-0 qOIqX" href="https://bitcoinops.org/en/topics/discreet-log-contracts/"><span data-offset-key="ducte-0-0"> Discreet Log Contracts (DLCs)</span></a><span data-offset-key="ducte-1-0"> </span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="1uvpm-0-0"><a class="sc-1bctqj2-0 qOIqX" href="https://bitcoinmagazine.com/technical/what-is-bitcoin-checktemplateverify"> <span data-offset-key="1uvpm-0-0">Explaining CheckTemplateVerify</span></a><span data-offset-key="1uvpm-1-0"> </span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="c4uhe-0-0"><a class="sc-1bctqj2-0 qOIqX" href="https://bitcoinmagazine.com/technical/noinput-class-bitcoin-soft-fork-simplify-lightning"> <span data-offset-key="c4uhe-0-0">The &#171;NoInput class&#187;</span></a><span data-offset-key="c4uhe-1-0"> </span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="5c31r-0-0"><a class="sc-1bctqj2-0 qOIqX" href="https://bitcoinmagazine.com/industry-events/bitcoin-2022"><span data-offset-key="5c31r-0-0"> Обзор конференции от Bitcoin Magazine</span></a><span data-offset-key="5c31r-1-0"> </span></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="fskqc-0-0"><a class="sc-1bctqj2-0 qOIqX" href="https://twitter.com/murchandamus/status/1509236724135870469"><span data-offset-key="fskqc-0-0"> Статистика типов адресов (1:00:30)</span></a></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="fhm19-0-0"><a class="sc-1bctqj2-0 qOIqX" href="https://bitcoinmagazine.com/industry-events/bitcoin-2022"><span data-offset-key="fhm19-0-0"> Обзор конференции от Bitcoin Magazine</span></a></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="1qff0-0-0"><a class="sc-1bctqj2-0 qOIqX" href="https://braiins.com/stratum-v2"><span data-offset-key="1qff0-0-0">Stratum v2</span></a></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="cphj8-0-0"><a class="sc-1bctqj2-0 qOIqX" href="https://bitcoinops.org/en/topics/musig/"><span data-offset-key="cphj8-0-0">MuSig</span></a></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="3ectv-0-0"><a class="sc-1bctqj2-0 qOIqX" href="../e131/index.html"><span data-offset-key="3ectv-0-0">ББ-131 о форках с Никитой Жаворонковым</span></a></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="6uoob-0-0"><a class="sc-1bctqj2-0 qOIqX" href="https://bitcoinwords.github.io/grants/"><span data-offset-key="6uoob-0-0">Bitcoin grant tracker (немного устарел)</span></a></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="2eqhi-0-0"><a class="sc-1bctqj2-0 qOIqX" href="https://adamjonas.com/bitcoin/funding/grants/grants-bitcoin-open-source/"> <span data-offset-key="2eqhi-0-0">A guide for bitcoin open-source grant seekers</span></a></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="7ueb6-0-0"><span data-offset-key="7ueb6-0-0">Bидео с конференции:</span>
<ul>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="6vqvc-0-0"><a class="sc-1bctqj2-0 qOIqX" href="https://www.youtube.com/playlist?list=PLe0djdakvnFZ2C7DMjQfiuqCtbxk0ZTsz"> <span data-offset-key="6vqvc-0-0">Main stage</span></a></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="283gc-0-0"><a class="sc-1bctqj2-0 qOIqX" href="https://www.youtube.com/playlist?list=PLe0djdakvnFYos9Vk3tTTywmLzZRyEZ_o"> <span data-offset-key="283gc-0-0">Open source stage</span></a></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="bug91-0-0"><a class="sc-1bctqj2-0 qOIqX" href="https://www.youtube.com/playlist?list=PLe0djdakvnFYvo8SU4JmycrjkxFoanBxc"> <span data-offset-key="bug91-0-0">Mining stage</span></a></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="99ebc-0-0"><a class="sc-1bctqj2-0 qOIqX" href="https://www.youtube.com/playlist?list=PLe0djdakvnFak5CW68QxHrpB1bPHq-gQY"> <span data-offset-key="99ebc-0-0">Enterprise stage</span></a></li>
<li class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr" data-offset-key="ha6m-0-0"><a class="sc-1bctqj2-0 qOIqX" href="https://www.youtube.com/playlist?list=PLe0djdakvnFbQsNfw75tKqJC9Q3tjsd8M"> <span data-offset-key="ha6m-0-0">Genesis stage</span></a></li>
</ul>
</li>
</ul>
<p class="p1">Спасибо нашим спонсорам:</p>
<ul class="ul1">
<li style="list-style-type: none;">
<ul class="ul1">
<li style="list-style-type: none;">
<ul class="ul1">
<li style="list-style-type: none;">
<ul class="ul1">
<li class="li1"><a href="https://app.1inch.io">1inch Network &#8212; агрегатор децентрализованных бирж</a></li>
<li class="li1"><a href="https://zerion.io/">Zerion &#8212; умный кошелёк для Web3-мира</a></li>
<li class="li1"><span class="s4"><a href="https://everscale.network/en/developers/grants">Everscale &#8212; асинхронный layer1-блокчейн</a><br />
</span></li>
</ul>
</li>
</ul>
</li>
</ul>
</li>
</ul>
<p class="p2"><a href="../donate/index.html"><span class="s4">Поддержите подкаст!</span></a></p>
<p class="p2"><span class="s5"><a href="../index.html">https://basicblockradio.com/</a></span></p>
