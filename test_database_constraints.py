env:
  HBEPA_DB_NAME: hbepa_sandbox
  HBEPA_DB_USER: hbepa_audit_user
  HBEPA_DB_PASSWORD: ${{ secrets.HBEPA_DB_PASSWORD }}
  HBEPA_DB_HOST: localhost
  HBEPA_DB_PORT: 5432
