��� ���������� ������ ���������� ���������� ��������� ���� requirements.txt.
�������� ���� ������ zen �������� pg_restore -d zen zen.dumps.
������� ��������� �������� �������� python3 zen_pipeline.py
����� ��������� �������: python3 zen_dashboard.py
��� ���������� � ����� ��������� ��������� ��������(crontab -e): * 23 * * * python3 zen_pipeline.py