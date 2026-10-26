ББ-088: Электронное голосование и блокчейн-выборы в Москве

<p>Обсуждаем электронное голосование и его имплементацию (на блокчейне!) на выборах в Мосгордуму 8 сентября 2019 года. Полную версию с разбором кода смарт-контрактов смотрите в <a href="https://youtu.be/4YzgwZ7ib4g">стриме</a>.</p>
<ul>
<li><span class="name" data-wfid="288a72a10d25">00:00 предисловие: чем всё закончилось</span></li>
<li><span class="name" data-wfid="5017481a8cd8">05:29 онлайн-голосование на московских выборах. Что? Да!</span></li>
<li><span class="name" data-wfid="08bf84f8906d">06:59 что такое выборы в Мосгордуму</span></li>
<li><span class="name" data-wfid="56da74f80c2d">19:10 идея электронных выборов витает в воздухе</span></li>
<li><span class="name" data-wfid="7932a58ab768">10:10 конфликтующие требования: анонимность и прозрачность</span></li>
<li><span class="name" data-wfid="62db1036b9ad">14:35 цель системы &#8212; усложнить фальсификации (нельзя полностью предотвратить)</span></li>
<li><span class="name" data-wfid="61363bc0f6a0">17:28 история электронного голосования</span></li>
<li><span class="name" data-wfid="1c65fbc5ee16">19:25 что предлагается у нас? главная проблема выборов в Москве &#8212; не в смарт-контрактах</span></li>
<li><span class="name" data-wfid="e07b347ac314">22:30 правильный подход к проектированию электронного голосования</span></li>
<li><span class="name" data-wfid="891395dab9e3">27:30 репозиторий moscow-technologies/blockchain-voting</span></li>
<li><span class="name" data-wfid="90169070563c">30:45 репозиторий выглядит как поделка?</span></li>
<li><span class="name" data-wfid="041b0e5d83ff">33:08 где будут крутиться ноды? Спойлер: на серверах ДИТ</span></li>
<li><span class="name" data-wfid="a74bdcc216d5">34:11 вопросы identity: ключевая проблема выборов</span></li>
<li><span class="name" data-wfid="99b10744f535">40:57 как французский ученый сломал московские выборы: о сложности комбинирования криптографических примитивов</span></li>
<li><span class="name" data-wfid="6f9d3f227c90">46:14 кто такой Сергей Павлин? 😉</span></li>
<li><span class="name" data-wfid="1a262ffee9bf">47:22 структура репозитория, программа тестирования / bug bounty</span></li>
<li><span class="name" data-wfid="afe5621b45bf">49:30 фронтент на PHP: нормально?</span></li>
<li><span class="name" data-wfid="7335f1041871">52:14 обзор директории smart-contracts, вопрос безопасности зависимостей</span></li>
<li><span class="name" data-wfid="f1279aacb813">57:02 имплементация криптографии на Javascript, шифрование El-Gamal</span></li>
<li><span class="name" data-wfid="2a64bd20aa5e">1:01:21 прекрасные цитаты из документа Мосгоризбиркома</span></li>
<li><span class="name" data-wfid="844b336ddc11">1:23:12 генерация и разделение приватного ключа. аналогии с Banana split и церемонией Zcash</span></li>
<li><span class="name" data-wfid="623e3ab81689">1:08:57 защита анонимности на сетевом уровне: прокси, случайные задержки и прочее</span></li>
<li><span class="name" data-wfid="167e25509cc5">1:09:45 разбор смарт-контрактов (полную версию смотрите в стриме)</span></li>
<li><span class="name" data-wfid="290d1fab3248">1:10:07 а был ли аудит? о важности независимой экспертизы</span></li>
<li><span class="name" data-wfid="6b73b9804264">1:12:40 почему важно разрешать менять голос, и проблема аналоговой дыры</span></li>
<li><span class="name" data-wfid="c92759620c32">1:16:25 самое главное: расшифровка бюллетеня! можно восстановить, кто как голосовал?</span></li>
<li><span class="name" data-wfid="7047c292420b">1:20:05 корень проблемы: нет спецификации или ТЗ</span></li>
<li><span class="name" data-wfid="7b31f368b65b">1:23:07 причём здесь Ричард Столлман</span></li>
<li><span class="name" data-wfid="2b690b7906c9">1:25:58 политические проблемы требуют политических решений</span></li>
<li><span class="name" data-wfid="56394b6540fa">1:29:15 про движ с муниципальными депутатами в Питере (Кац предлагает победить)</span></li>
<li><span class="name" data-wfid="09280653d611">1:31:49 поддерживаем технологическую продвинутость государства (но есть и тёмная сторона)</span></li>
<li><span class="name" data-wfid="a55f357b8523">1:38:25 под занавес переслушиваем бессмертный хит Сергея Шнурова</span></li>
</ul>
<p>Ссылки:</p>
<ul>
<li><a href="https://www.mos.ru/news/item/61790073/"><span class="name" data-wfid="a55f357b8523">В столице завершилось электронное голосование на выборах в Мосгордуму</span></a></li>
<li><a href="http://www.vybory.izbirkom.ru/region/izbirkom?action=show&amp;vrn=27720002327736&amp;region=77&amp;prver=0&amp;pronetvd=null"> Официальные результаты выборов</a></li>
<li><a href="http://www.mosgorizbirkom.ru/documents/10279/19437521/rs_112_4.pdf/6569509f-3c35-4562-b337-e58988071d7c"> Документ Мосгоризбиркома</a></li>
<li><a href="https://github.com/moscow-technologies/blockchain-voting">https://github.com/moscow-technologies/blockchain-voting</a></li>
<li><a href="https://www.golosinfo.org/articles/143686">Отчёт &#171;Голоса&#187; о финальном тестировании электронного голосования</a></li>
<li><a href="https://www.youtube.com/watch?v=w3_0x6oaDmI">Why Electronic Voting is a BAD Idea &#8212; Computerphile</a></li>
<li><a href="https://meduza.io/feature/2019/09/06/meriya-obeschala-prozrachnoe-internet-golosovanie-v-moskve-v-itoge-ona-mozhet-opublikovat-lyubye-rezultaty-i-proverit-ih-nikto-ne-smozhet"> Мэрия обещала прозрачное интернет-голосование в Москве&#8230;</a></li>
<li><a href="https://meduza.io/cards/kriptograf-vzlomal-sistemu-internet-golosovaniya-v-moskve-my-tozhe-eto-sdelali-i-vy-tozhe-mozhete"> Криптограф взломал систему интернет-голосования в Москве</a></li>
<li><a href="https://meduza.io/news/2019/09/10/kandidat-v-mosgordumu-roman-yuneman-podal-v-izbirkom-zhalobu-na-itogi-internet-golosovaniya-v-svoem-okruge"> Кандидат в депутаты Мосгордумы Роман Юнеман обжаловал итоги интернет-голосования в своем округе</a></li>
<li><a href="https://xkcd.com/2030/">Obligatory XKCD</a>. Wear gloves.</li>
</ul>
<p>Поддержите подкаст!</p>
<ul>
<li>Bitcoin: bc1qec856uhwuguhnn28r54tlkrh3dh95ctajvpjaf</li>
<li>Patreon: <a href="https://www.patreon.com/basicblockradio/overview">https://www.patreon.com/basicblockradio/overview</a></li>
</ul>
<p>Спонсор подкаста &#8212; <a href="https://wavesplatform.com/">Waves</a>. Спасибо!</p>
<p><a href="../index.html">basicblockradio.com</a></p>
