import React, { useState } from 'react';
import { View, Text, Button, TextInput, Platform } from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import { useNavigation } from '@react-navigation/native';
import { useUploadNota } from '@/services/queries';

export default function UploadNotaScreen() {
  const [cnpj, setCnpj] = useState('');
  const [file, setFile] = useState<{ uri: string; name: string; type: string } | null>(null);
  const nav = useNavigation<any>();
  const { mutateAsync, isPending } = useUploadNota();

  async function pickFile() {
    const res = await DocumentPicker.getDocumentAsync({ multiple: false });
    if (res.assets && res.assets[0]) {
      const a = res.assets[0];
      setFile({ uri: a.uri, name: a.name || 'nota', type: a.mimeType || 'application/octet-stream' });
    }
  }

  async function onSubmit() {
    if (!file || !cnpj) return;
    const out = await mutateAsync({ file, meu_cnpj: cnpj });
    nav.navigate('JobStatus', { uuid: out.uuid });
  }

  return (
    <View style={{ padding: 16, gap: 12 }}>
      <Text>Selecione o arquivo da Nota Fiscal</Text>
      <Button title={file ? `Selecionado: ${file.name}` : 'Escolher arquivo'} onPress={pickFile} />
      <Text>Informe o CNPJ da sua empresa</Text>
      <TextInput
        value={cnpj}
        onChangeText={setCnpj}
        placeholder="CNPJ"
        keyboardType={Platform.OS === 'ios' ? 'numbers-and-punctuation' : 'number-pad'}
        style={{ borderWidth: 1, borderColor: '#ddd', padding: 8, borderRadius: 6 }}
      />
      <Button title={isPending ? 'Enviando...' : 'Processar Nota'} disabled={!file || !cnpj || isPending} onPress={onSubmit} />
    </View>
  );
}
