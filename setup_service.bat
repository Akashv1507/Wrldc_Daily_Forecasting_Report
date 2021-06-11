call nssm.exe install mis_forecasting_report "%cd%\run_server.bat"
rem call nssm.exe edit mis_forecasting_report
call nssm.exe set mis_forecasting_report AppStdout "%cd%\logs\mis_forecasting_report.log"
call nssm.exe set mis_forecasting_report AppStderr "%cd%\logs\mis_forecasting_report.log"
call sc start mis_forecasting_report