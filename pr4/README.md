# Практическая работа № 4. Анализаторы кода

Папка содержит исходную и изменённые версии системы библиотеки (Python), учебный конвертер (Java), проверочные программы и протоколы запусков.

- python/baseline и java/baseline — исправные версии;
- static_faults — копии с пятью изменениями для статического анализа;
- dynamic_faults — независимые копии с тремя дефектами для динамических проверок;
- results — полные текстовые протоколы и записи JFR;
- Report_PR4_Frolov.docx — отчёт с листингами.

Python: для каждого варианта выполнить `python python/dynamic_check.py python/baseline` либо `python python/dynamic_check.py python/dynamic_faults`; для статической проверки установить pylint, ruff, bandit и запустить соответствующие инструменты по файлу library_manager.py. Группы Ruff: E,F,N,S,B.

Java: с установленным JDK выполнить `javac -d out java/baseline/Converter.java java/Probe.java java/RuntimeMonitor.java`, затем `java -cp out RuntimeMonitor`. Для второй версии заменить baseline на dynamic_faults и компилировать в отдельный каталог. JFR запускать через `java -XX:StartFlightRecording=filename=run.jfr,settings=profile -cp out Probe`, результат просмотреть `jfr summary run.jfr`. Checkstyle использовался с /google_checks.xml, PMD — category/java/bestpractices.xml и category/java/errorprone.xml, SpotBugs — по Converter.class с -effort:max -low.

Показатели времени и памяти зависят от компьютера. Анализаторы и сценарии проверяют только выбранные правила и входы. Для дефектных копий отрицательные результаты ожидаемы.
