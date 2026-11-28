# Практическая работа № 4 — анализаторы кода

Здесь находятся программы, на которых можно повторить проверки из работы.
Исходные версии `python/baseline` и `java/baseline` исправны по выбранным контрольным сценариям.
`static_faults` содержит пять намеренных изменений для статического анализа;
`dynamic_faults` — отдельную копию с тремя намеренными дефектами поведения.
Эти дефекты сохранены для сравнения, их не следует переносить в исходную версию.

## Быстрый запуск из папки pr4

Нужны Python 3.11+ и **JDK 17+** (не JRE). При первой настройке нужен интернет.

```powershell
cd pr4
python run_checks.py --setup
python run_checks.py --group all --java-home 'C:/путь/к/jdk'
```

Вместо `--java-home` можно задать `JAVA_HOME` или добавить `java`, `javac` и `jfr`
из одного JDK в `PATH`. Скрипт компилирует Java с `--release 17`.
Инструменты скачиваются в `.tools`, сборки находятся в `build`; эти папки не коммитятся.
Версии анализаторов закреплены: Pylint 4.1.4, Ruff 0.17.6, Bandit 1.9.4,
Checkstyle 10.21.4, PMD 6.55.0, SpotBugs 4.9.3.

Результат: `results/rerun/index.html` — открой этот файл в браузере.
Рядом находятся полные протоколы команд с кодами завершения, `.prof`, `.jfr` и
`manifest.json` с версиями, временем запуска, SHA-256 исходников и скачанных инструментов.
Старые протоколы непосредственно в `results` относятся к предыдущему запуску.
Отчёт Word и старый ZIP в этой папке оставлены без изменения и не являются
обновлённым комплектом кода; актуальные команды находятся в этом README.

## Что показать на защите

- `python/dynamic_check.py`: реальный cProfile, текущая/пиковая память tracemalloc,
  три строки с наибольшими выделениями и три независимых сценария поведения.
  Нагрузка — 2000 книг и 100 поисков **по названию**, чтобы проверялся поиск фрагмента.
- `java/Probe.java`: ожидаемые и фактические результаты трёх конвертаций;
  отдельная нагрузка из 20 000 000 преобразований.
- `java/RuntimeMonitor.java`: `MemoryMXBean` и `ThreadMXBean` через API JMX,
  измерение кучи и CPU текущего потока, запись JFR того же запуска.
  Запись содержит событие `pr4.Workload` с длительностью, числом итераций и checksum.
  Сведения о переменных окружения и аргументах JVM не записываются.
- `run_checks.py`: одинаковые правила для исходной и изменённой версии, раздельные
  каталоги сборки и новые процессы Python, чтобы версии не смешивались.
- `results/rerun/*.txt`: точные команды и фактический вывод каждого инструмента.

## Отдельные проверки

```powershell
python run_checks.py --group dynamic --java-home 'C:/путь/к/jdk'
python run_checks.py --group static --java-home 'C:/путь/к/jdk'
python run_checks.py --group all --language python
```

Каждый запуск обновляет свои файлы в `results/rerun`. Для единого протокола всех
проверок используй `--group all`.

Без общего скрипта динамический анализ можно показать так (из папки pr4):

```powershell
python python/dynamic_check.py python/baseline --profile baseline.prof
python python/dynamic_check.py python/dynamic_faults --profile faulty.prof --expect-failures 3
javac --release 17 -encoding UTF-8 -d build/baseline java/baseline/Converter.java java/Probe.java java/RuntimeMonitor.java
java -cp build/baseline RuntimeMonitor baseline.jfr 0
jfr summary baseline.jfr
jfr print --events pr4.Workload baseline.jfr
```

Для Java с дефектами компилируй `java/dynamic_faults/Converter.java` в отдельную
папку `build/dynamic_faults`, затем передай `RuntimeMonitor` имя JFR-файла и число `3`.

`PASS/FAIL` выдают контрольные сценарии, а не профилировщики.
В baseline ожидаются 3 PASS, в dynamic_faults — 3 FAIL для каждого языка.
Параметр ожидаемых отказов нужен общему запуску для проверки учебного примера;
он не превращает FAIL сценария в PASS. Без него дефектная версия завершится с ошибкой.
Показатели памяти и времени меняются от запуска к запуску; разность кучи не доказывает утечку.

Статический анализ ограничен `library_manager.py` и `Converter.java`.
Ruff запускается с `E,F,N,S,B`, Checkstyle — с `/google_checks.xml`,
PMD — с `bestpractices,errorprone`, SpotBugs — по `Converter.class`, `-effort:max -low`.
Количество сообщений не равно количеству независимых дефектов. Наличие замечаний
в исходном коде ожидаемо и не означает ошибку выбранных функциональных сценариев.
`MonitorProbe.java` — дополнительная старая нагрузка для ручного мониторинга;
в основной запуск не входит. `jstat` не используется как успешно выполненная проверка.
