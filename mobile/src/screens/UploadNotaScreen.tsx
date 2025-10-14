import React, { useState } from 'react';
import { View, Text, Button, TextInput, Platform } from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import { useNavigation } from '@react-navigation/native';
import { useUploadNota } from '../hooks/api';
import { showMessage } from 'react-native-flash-message';

export default function UploadNotaScreen() {
  const [cnpj, setCnpj] = useState('');
  const [file, setFile] = useState<{ uri: string; name: string; type: string } | null>(null);
  const nav = useNavigation<any>();
  const { mutateAsync, isPending } = useUploadNota();

  async function pickFile() {
    console.log('[UploadNotaScreen] Iniciando seleção de arquivo');
    const res = await DocumentPicker.getDocumentAsync({ multiple: false });
    if (res.assets && res.assets[0]) {
      const a = res.assets[0];
      console.log('[UploadNotaScreen] Arquivo selecionado:', { name: a.name, size: a.size, mimeType: a.mimeType });
      setFile({ uri: a.uri, name: a.name || 'nota', type: a.mimeType || 'application/octet-stream' });
    } else {
      console.log('[UploadNotaScreen] Nenhum arquivo selecionado');
    }
  }

  async function onSubmit() {
    if (!file) return;
    console.log('[UploadNotaScreen] Iniciando upload da nota fiscal', { fileName: file.name, cnpj: cnpj || 'não informado' });
    try {
      const data: any = { file };
      if (cnpj) data.meu_cnpj = cnpj;
      const out = await mutateAsync(data);
      console.log('[UploadNotaScreen] Upload concluído com sucesso', { job_uuid: out.job_uuid, message: out.message });
      showMessage({
        message: out.message,
        type: 'success',
      });
      nav.navigate('JobStatus', { uuid: out.job_uuid });
    } catch (error: any) {
      console.error('[UploadNotaScreen] Erro no upload da nota fiscal', { error: error.message, response: error.response?.data });
      showMessage({
        message: error.response?.data?.detail || 'An error occurred',
        type: 'danger',
      });
    }
  }

  return (
    <View style={{ padding: 16, gap: 12 }}>
      <Text>Selecione o arquivo da Nota Fiscal</Text>
      <Button title={file ? `Selecionado: ${file.name}` : 'Escolher arquivo'} onPress={pickFile} />
      <Text>Informe o CNPJ da sua empresa (opcional)</Text>
      <TextInput
        value={cnpj}
        onChangeText={setCnpj}
        placeholder="CNPJ (opcional)"
        keyboardType={Platform.OS === 'ios' ? 'numbers-and-punctuation' : 'number-pad'}
        style={{ borderWidth: 1, borderColor: '#ddd', padding: 8, borderRadius: 6 }}
      />
      <Button title={isPending ? 'Enviando...' : 'Processar Nota'} disabled={!file || isPending} onPress={onSubmit} />
    </View>
  );
}
