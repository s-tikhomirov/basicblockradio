ББ-195: Гурген Аракелов (Fair Math) о криптографических основах FHE

<p dir="ltr">Гурген Аракелов – CEO Fair Math и специалист по полностью гомоморфному шифрованию (fully homomorphic encryption, FHE). FHE позволяет производить произвольные вычисления над зашифрованными данными. За последние несколько лет алгоритмы FHE вплотную приблизились к возможности внедрения в реальные продукты, в том числе в блокчейн-протоколах.</p>
<p dir="ltr">В первой части разговора с Гургеном обсуждаем теоретические основы FHE: криптографию на решётках, удаление шума без расшифровки (бутстреппинг) и применение FHE в сочетании с ZK и MPC.</p>
<p><strong> </strong></p>
<p><strong>Таймкоды:</strong></p>
<ul>
<li>04:15 – как Гурген пришёл в блокчейн: диссертация по FHE и работа с медицинскими данными</li>
<li>07:00 – гость и ведущие ностальгируют по распределённым вычислениям BOINC</li>
<li>09:50 – бюрократические сложности внедрения FHE в медицине</li>
<li>13:40 – теоретические основы и история FHE</li>
<li>18:40 – ранние работы по FHE и прорыв Крейга Джентри 2009 года</li>
<li>23:00 – как работает бутстреппинг и откуда берётся шум при шифровании</li>
<li>28:00 – почему шум растёт при повторных гомоморфных операциях</li>
<li>31:10 – уменьшение шума в схеме Джентри: расшифровка &#171;внутри коробочки&#187;</li>
<li>45:10 – криптография на решётках</li>
<li>47:10 – задача обучения с ошибками (Learning with Errors, LWE)</li>
<li>55:30 – квантовая устойчивость криптографии на решётках</li>
<li>57:25 – чем FHE отличается от ZK?</li>
<li>1:00:00 – как использовать ZK с комбинации с FHE</li>
<li>1:03:05 – почему для генерации ZK-пруфа нужно раскрывать схему вычислений</li>
<li>1:04:10 – как MPC соотносится с ZK и FHE</li>
<li>1:07:20 – производительность FHE</li>
<li>1:12:00 – применения FHE в блокчейн-индустрии</li>
<li>1:15:00 – все узлы FHE-блокчейна должны иметь общий ключ?</li>
<li>1:23:10 – использование MPC для разделения общего ключа в FHE-EVM</li>
<li>1:29:00 – проблемы безопасности в MPC-схемах (в т.ч. long-range attacks)</li>
<li>1:35:55 – тонкости применения шифрования в ride-hailing</li>
<li>1:38:40 – верифицируемость вычислений и применение ZK вместе с FHE</li>
</ul>
<p><strong> </strong></p>
<p><strong>Ссылки:</strong></p>
<ul>
<li>Ресурсы Fair Math: <a href="https://fairmath.xyz/">сайт</a>, <a href="https://x.com/FairMath">твиттер</a>, <a href="https://github.com/fairmath">гитхаб</a></li>
<li><a href="https://eprint.iacr.org/2024/1917">Fair Math Whitepaper</a></li>
<li><a href="https://eprint.iacr.org/2024/612">FHERMA Whitepaper</a></li>
<li><a href="https://x.com/g_arakelov">Твиттер Гургена</a></li>
<li>Доклады Гургена:</li>
<li style="list-style-type: none;">
<ul>
<li dir="ltr" role="presentation"><a href="https://www.youtube.com/watch?v=sjK7eM1b_ks">Decentralized FHE computer</a> (2024)</li>
</ul>
</li>
<li style="list-style-type: none;">
<ul>
<li dir="ltr" role="presentation"><a href="https://www.youtube.com/watch?v=9dvVxbxUmGo">Scalable MLIR-based FHE compiler</a> (2024)</li>
</ul>
</li>
<li><a href="https://github.com/jonaschn/awesome-he">Awesome HE</a> &#8212; сборник ресурсов по гомоморфному шифрованию</li>
<li><a href="https://intensecrypto.org/public/lec_15_FHE.html">Fully homomorphic encryption: Introduction and bootstrapping</a></li>
<li><a href="https://medium.com/inception-capital/the-next-frontier-in-digital-privacy-that-were-excited-about-999f54404c16"> The Next Frontier in Digital Privacy &#8212; Inception Capital</a></li>
<li><a href="https://medium.com/inception-capital/investing-in-fair-math-33a2accd8592"> Investing in Fair Math &#8212; Inception Capital</a></li>
<li><a href="https://medium.com/alliancedao/zkps-fhe-mpc-managing-private-state-in-blockchains-17cc3661007d"> ZKPs, FHE, MPC: Managing Private State in Blockchains &#8212; Mohamed Fouda (Alliance)</a></li>
<li>Zero Knowledge Podcast: <a href="https://zeroknowledge.fm/248-2/">Episode 248: Revisiting FHE with Rand Hindi from Zama</a></li>
<li>Zero Knowledge Podcast: <a href="https://zeroknowledge.fm/270-2/">Episode 270: FHE and ZKPs with Sunscreen&#8217;s Ravital Solomon</a></li>
<li><a href="https://www.youtube.com/watch?v=487AjvFW1lk">A Decade (or so) of fully homomorphic encryption, by Craig Gentry</a></li>
<li><a href="https://www.cybersecurity.blog.aisec.fraunhofer.de/en/a-somewhat-gentle-introduction-to-lattice-based-post-quantum-cryptography/"> A (somewhat) gentle introduction to lattice-based post-quantum cryptography</a></li>
<li><a href="https://machinelearning.apple.com/research/homomorphic-encryption"> Использование FHE в Apple</a></li>
<li><a href="https://eurocrypt.iacr.org/2021/slides/gentry.pdf">Презентация Craig Gentry (Eurocrypt 2021)</a></li>
<li><a href="https://www.youtube.com/watch?v=184NHhE3Kq0">FHE: Past, present and future &#8212; Craig Gentry (2024)</a></li>
</ul>
<p dir="ltr"><strong>Спасибо нашим спонсорам!</strong></p>
<ul>
<li><a href="https://t.me/cp0xdotcom">cp0x</a> – русскоязычное комьюнити, делегат и валидатор</li>
<li><a href="https://zerion.io/">Zerion</a> – умный кошелек для Web3-мира</li>
<li><a href="https://powerpool.finance/power-agent/">PowerPool</a> – автоматизация исполнения любых ончейн-действий и стратегий в Defi/Web3</li>
<li><a href="https://www.ackinacki.com/">Acki Nacki</a> от GOSH – the fastest blockchain possible</li>
</ul>
<p>Поддержите подкаст! <a href="../donate/index.html">https://basicblockradio.com/donate/</a></p>
<p dir="ltr">Заходите в наш чат: <a href="https://t.me/basicblockradio_chat">https://t.me/basicblockradio_chat</a></p>
<p dir="ltr">Наш сайт: <a href="../index.html">https://basicblockradio.com/</a></p>
<p><strong> </strong></p>
