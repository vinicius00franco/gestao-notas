import React, { useMemo, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Modal } from 'react-native';
import { useCalendarResumo, useCalendarDia } from '../hooks/api';
import { formatCurrencyBRL } from '../utils/format';

function daysInMonth(year: number, month: number) {
  return new Date(year, month, 0).getDate();
}

export default function CalendarDashboard({ initialDate = new Date() }: { initialDate?: Date }) {
  const [viewDate, setViewDate] = useState(initialDate);
  const ano = viewDate.getFullYear();
  const mes = viewDate.getMonth() + 1;
  const { data } = useCalendarResumo(ano, mes);
  const mapaDias = useMemo(() => {
    const m = new Map<string, { valor_pagar?: number; valor_receber?: number; saldo?: number }>();
    data?.dias.forEach((d: any) => m.set(d.data, d));
    return m;
  }, [data]);

  const [selected, setSelected] = useState<string | null>(null);
  const detalhes = useCalendarDia(selected || '');

  const totalDays = daysInMonth(ano, mes);
  const firstWeekDay = new Date(ano, mes - 1, 1).getDay();

  const prevMonth = () => setViewDate(new Date(ano, mes - 2, 1));
  const nextMonth = () => setViewDate(new Date(ano, mes, 1));

  const renderCell = (day: number) => {
    const iso = new Date(ano, mes - 1, day).toISOString().slice(0, 10);
    const resumo = mapaDias.get(iso);
    let label = '';
    if (resumo) {
      if (resumo.saldo !== undefined) label = `Saldo ${formatCurrencyBRL(resumo.saldo)}`;
      else if (resumo.valor_pagar !== undefined) label = `Pagar ${formatCurrencyBRL(resumo.valor_pagar)}`;
      else if (resumo.valor_receber !== undefined) label = `Receber ${formatCurrencyBRL(resumo.valor_receber)}`;
    }
    return (
      <TouchableOpacity key={day} style={styles.cell} onPress={() => setSelected(iso)}>
        <Text style={styles.day}>{day}</Text>
        {!!label && <Text style={styles.value}>{label}</Text>}
      </TouchableOpacity>
    );
  };

  const cells = [] as React.ReactNode[];
  for (let i = 0; i < firstWeekDay; i++) cells.push(<View key={`e${i}`} style={styles.cellEmpty} />);
  for (let d = 1; d <= totalDays; d++) cells.push(renderCell(d));

  return (
    <View style={{ flex: 1 }}>
      <View style={styles.header}>
        <TouchableOpacity onPress={prevMonth}><Text style={styles.nav}>{'<'}</Text></TouchableOpacity>
        <Text style={styles.title}>{ano}-{String(mes).padStart(2, '0')}</Text>
        <TouchableOpacity onPress={nextMonth}><Text style={styles.nav}>{'>'}</Text></TouchableOpacity>
      </View>
      <View style={styles.grid}>{cells}</View>

      <Modal visible={!!selected} transparent animationType="slide" onRequestClose={() => setSelected(null)}>
        <View style={styles.modalWrap}>
          <View style={styles.sidePanel}>
            <View style={styles.panelHeader}>
              <Text style={styles.panelTitle}>{selected}</Text>
              <TouchableOpacity onPress={() => setSelected(null)}><Text style={styles.close}>Fechar</Text></TouchableOpacity>
            </View>
            <ScrollView>
              {detalhes.data?.detalhes.map((it: any, idx: number) => (
                <View key={idx} style={styles.item}>
                  <Text style={styles.itemTitle}>{it.nome_fantasia}</Text>
                  <Text style={styles.itemSub}>{it.cnpj}</Text>
                  <Text style={styles.itemRight}>{formatCurrencyBRL(it.valor)} {it.tipo ? `(${it.tipo})` : ''}</Text>
                </View>
              ))}
              {!detalhes.data?.detalhes?.length && <Text style={{ padding: 12 }}>Sem lançamentos</Text>}
            </ScrollView>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: 'row', justifyContent: 'space-between', padding: 12, alignItems: 'center' },
  nav: { fontSize: 20, fontWeight: '700' },
  title: { fontSize: 16, fontWeight: '700' },
  grid: { flexDirection: 'row', flexWrap: 'wrap' },
  cell: { width: '14.28%', borderWidth: StyleSheet.hairlineWidth, borderColor: '#ddd', padding: 4 },
  cellEmpty: { width: '14.28%', borderWidth: 0, padding: 4 },
  day: { fontWeight: '700' },
  value: { fontSize: 10, marginTop: 4 },
  modalWrap: { flex: 1, backgroundColor: 'rgba(0,0,0,0.2)', justifyContent: 'flex-end' },
  sidePanel: { height: '60%', backgroundColor: 'white', borderTopLeftRadius: 12, borderTopRightRadius: 12 },
  panelHeader: { flexDirection: 'row', justifyContent: 'space-between', padding: 12, borderBottomWidth: StyleSheet.hairlineWidth },
  panelTitle: { fontWeight: '700' },
  close: { color: '#7d3cff', fontWeight: '700' },
  item: { padding: 12, borderBottomWidth: StyleSheet.hairlineWidth, borderBottomColor: '#eee' },
  itemTitle: { fontWeight: '700' },
  itemSub: { color: '#777', marginTop: 2 },
  itemRight: { position: 'absolute', right: 12, top: 12, fontWeight: '700' },
});
