ББ-082: Алекс Скиданов (NEAR) о шардинге в блокчейнах и спортивном программировании

<p>Алекс Скиданов &#8212; сооснователь NEAR. NEAR protocol решает проблему масштабирования с помощью шардинга и proof-of-stake. До перехода в блокчейн-индустрию Алекс побеждал на чемпионате мира по программированию ACM ICPC и был первым сотрудником MemSQL. Обсуждаем отличия спортивного программирования от промышленного, эволюцию баз данных и масштабирование блокчейнов. Шардированные протоколы с proof-of-stake сталкиваются со множеством новых проблем: как NEAR их решает?</p>
<ul>
<li><span class="name" data-wfid="39e588820f50">00:30 спортивное программирование и победы на ACM ICPC</span></li>
<li><span class="name" data-wfid="ea14e53f655a">01:55 отличия спортивного программирования от промышленного, вредные привычки спортивных программистов</span></li>
<li><span class="name" data-wfid="c2045c1cde94">04:50 почему программисты из России так часто выигрывают чемпионат мира?</span></li>
<li><span class="name" data-wfid="138fffd1b0e9">05:36 чем чемпионат по программированию отличается от хакатона?</span></li>
<li><span class="name" data-wfid="f8c0bbacaaa1">07:51 работа Алекса в MemSQL: как разработать очень быструю базу данных?</span></li>
<li><span class="name" data-wfid="2f740d542676">12:21 развитие индустрии баз данных: прогресс остановился?</span></li>
<li><span class="name" data-wfid="49f7b43dcbc4">14:29 мир стартапов в Кремниевой Долине: компания Алекса в Y Combinator</span></li>
<li><span class="name" data-wfid="3ed5466dfc5d">18:02 зачем делать ещё один блокчейн-стартап?</span></li>
<li><span class="name" data-wfid="05d0f8ababdf">21:15 три школы масштабирования блокчейнов. &#171;Solana ушла настолько вперёд, что в плане скорости её не догнать&#187; (если все узлы валидируют всё)</span></li>
<li><span class="name" data-wfid="1f1f0d8d60b8">25:01 Layer-2 для масштабирования: каналы, сайдчейны, rollups</span></li>
<li><span class="name" data-wfid="9113a4bb2d40">26:34 Подход NEAR к масштабированию: шардинг</span></li>
<li><span class="name" data-wfid="aac504ef8bb0">28:42 почему &#171;наивный&#187; подход для шардированных систем требует слишком много доверия</span></li>
<li><span class="name" data-wfid="838eec8171a7">29:01 стандартный подход: выбирать валидаторов на шарды рандомно, чтобы нельзя было сконцентрировать стейк</span></li>
<li><span class="name" data-wfid="d3dc9d85e564">31:27 откуда берётся рандом? Threshold relays (Dfinity) и RANDAO + VDF (Ethereum)</span></li>
<li><span class="name" data-wfid="8891c06402a3">34:11 моделирование времени в proof-of-stake: можно ли верить часам валидаторов?</span></li>
<li><span class="name" data-wfid="9f8d5f464f2d">35:50 архитектура NEAR и три типа атак на шардированные proof-of-stake-системы. Невалидный переход и доступность данных</span></li>
<li><span class="name" data-wfid="5cb5f6c133aa">41:16 что делать, если всё-таки обнаружится заголовок невалидного блока на beacon chain?</span></li>
<li><span class="name" data-wfid="d3a4f3a96940">42:50 как ограничить ущерб, если один шард скомпрометирован? &#171;Social consensus это всегда дорого и неприятно&#187;</span></li>
<li><span class="name" data-wfid="e8921a948389">44:13 проблема доступности данных (data availability)</span></li>
<li><span class="name" data-wfid="fbb6fdf926fd">45:26 вопрос от Дмитрия Ховратовича: делаете ли proof of custody и какой? Адаптивный злоумышленник и быстрое перебрасывание валидаторов между шардами для проверки доступности данных</span></li>
<li><span class="name" data-wfid="53cac77732ae">49:43 аналогия с miner&#8217;s dilemma</span></li>
<li><span class="name" data-wfid="bbb806e766a7">50:21 решение Ethereum: последний бит от хеша блока плюс коммитмента, валидация блоков без стейта</span></li>
<li><span class="name" data-wfid="b876b00de591">52:41 вопрос от Егора Хомякова: какая модель безопасности? Что валидаторы могут делать плохого? Предположения: максимум 33% византийских узлов, максимум 50% офлайн (по стейку)</span></li>
<li><span class="name" data-wfid="c0f2ae347f7d">55:55 система мотивации в proof-of-stake: циклический аргумент?</span></li>
<li><span class="name" data-wfid="bdb2250ec49f">57:36 почему не proof-of-work?</span></li>
<li><span class="name" data-wfid="9b6e3d5c18b8">59:01 дизайн-пространство proof-of-stake: разные протоколы сойдутся к одному? Проблема DPOS</span></li>
<li><span class="name" data-wfid="369791b2d164">1:01:03 как NEAR решает data availability с помощью erasure code</span></li>
<li><span class="name" data-wfid="2288bfd7b00f">1:06:20 сложные протоколы увеличивают поверхность атаки?</span></li>
<li><span class="name" data-wfid="87139fa946fa">1:09:31 контракты в NEAR: WASM и Typescript; опасность &#171;простых&#187; языков и Rust</span></li>
<li><span class="name" data-wfid="bed2aa8d6c01">1:13:15 проблемы какой сложности имеет смысл класть на блокчейн?</span></li>
<li><span class="name" data-wfid="81959e02da9a">1:15:00 проблема оракулов и постонная цена газа</span></li>
<li><span class="name" data-wfid="6432ca86a711">1:16:16 какую проблему решает NEAR?</span></li>
<li><span class="name" data-wfid="c2aeedad046d">1:17:56 кому и зачем нужны децентрализованные технологии? Будущее DeFi и Web3</span></li>
<li><span class="name" data-wfid="b3e8e079e2a0">1:19:52 максимально оптимистичный сценарий для блокчейнов и для NEAR</span></li>
<li><span class="name" data-wfid="42c1a65969da">1:21:33 NEAR как централизованная компания и децентрализованный протокол &#8212; есть ли противоречие? Планы передачи контроля сообществу, выкатывание обновлений, on-chain governance</span></li>
<li><span class="name" data-wfid="bd515c8c4a53">1:24:47 ближайшие планы: запуск тестнета (скоро) и мейннета (1 ноября)</span></li>
</ul>
<p><span class="name" data-wfid="bd515c8c4a53">Ссылки:</span></p>
<ul>
<li><a href="https://nearprotocol.com/"><span class="name" data-wfid="bd515c8c4a53">NEAR protocol</span></a></li>
<li><a href="https://www.youtube.com/watch?v=UTs9ZkX401M">&#8216;Sharding Research&#8217; by Alex Skidanov</a> (видео)</li>
<li><a href="https://nearprotocol.com/blog/the-beginners-guide-to-the-near-blockchain/"> The Beginner&#8217;s Guide to the NEAR Blockchain</a></li>
<li><a href="https://www.youtube.com/playlist?list=PL9tzQn_TEuFWweVbfTbaedFdwVrvaYPq4"> Whiteboard Series with NEAR</a></li>
</ul>
<p>Поддержите подкаст!</p>
<ul>
<li><span class="name" data-wfid="290996cbdda5">Bitcoin: bc1qec856uhwuguhnn28r54tlkrh3dh95ctajvpjaf</span></li>
<li><span class="name" data-wfid="fe20ee9dc198">Patreon: <a class="contentLink" href="https://www.patreon.com/basicblockradio/overview" target="_blank" rel="noopener noreferrer">https://www.patreon.com/basicblockradio/overview</a></span></li>
</ul>

<p><a href="../index.html">basicblockradio.com</a></p>
