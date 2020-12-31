from django.core.files.storage import default_storage
default_storage.exists('storage_test')

file = default_storage.open('storage_test', 'w')
file.write('storage contents')
file.close()

default_storage.exists('storage_test')

file = default_storage.open('storage_test', 'r')
file.read()

file.close()

default_storage.delete('storage_test')
default_storage.exists('storage_test')
