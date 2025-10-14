import React, { useMemo, useState } from 'react';
import { View, StyleSheet, Modal, Text, TouchableOpacity, ScrollView } from 'react-native';
import { Calendar, LocaleConfig } from 'react-native-calendars';
import { useTheme } from '@/theme/ThemeProvider';
import { useCalendarResumo, useCalendarDia } from '../hooks/api';
import { formatCurrencyBRL } from '../utils/format';

// Configure Portuguese locale once
LocaleConfig.locales['pt-br'] = {
  monthNames: [
    'Janeiro',
    'Fevereiro',
    'Março',
    'Abril',
    'Maio',
    'Junho',
    'Julho',
    'Agosto',
    'Setembro',
    'Outubro',
    'Novembro',
    'Dezembro',
  ],
  monthNamesShort: [
    'Jan',
    'Fev',
    'Mar',
    'Abr',
    'Mai',
    'Jun',
    'Jul',
    'Ago',
    'Set',
    'Out',
    'Nov',
    'Dez',
  ],
  dayNames: ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'],
  dayNamesShort: ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'],
  today: 'Hoje',
};
LocaleConfig.defaultLocale = 'pt-br';

const formatDate = (d: Date) => d.toISOString().slice(0, 10);

type DateData = { dateString: string; day: number; month: number; year: number; timestamp: number };
type MarkedDates = Record<string, any>;

const CalendarScreen = () => {
  const { colors, spacing, typography } = useTheme();
  const [selected, setSelected] = useState<string>(formatDate(new Date()));
  const [currentYear, setCurrentYear] = useState<number>(new Date().getFullYear());
  const [currentMonth, setCurrentMonth] = useState<number>(new Date().getMonth() + 1);
  const [modalVisible, setModalVisible] = useState<boolean>(false);

  const { data: resumoData } = useCalendarResumo(currentYear, currentMonth);
  const { data: diaData } = useCalendarDia(selected);

  const markedDates: MarkedDates = useMemo(() => {
    const marks: MarkedDates = {
      [selected]: {
        selected: true,
        selectedColor: colors.primary,
        selectedTextColor: colors.onPrimary,
      },
    };

    // Add financial data dots
    resumoData?.dias.forEach((dia) => {
      const dots = [];
      if (dia.valor_pagar) {
        dots.push({ color: colors.error });
      }
      if (dia.valor_receber) {
        dots.push({ color: colors.secondary });
      }
      if (dots.length > 0) {
        marks[dia.data] = {
          ...marks[dia.data],
          dots,
        };
      }
    });

    return marks;
  }, [selected, colors.primary, colors.onPrimary, colors.error, colors.secondary, resumoData]);

  const calendarTheme = useMemo(
    () => ({
      calendarBackground: colors.background,
      monthTextColor: colors.text,
      textSectionTitleColor: colors.placeholder, // week day header
      arrowColor: colors.primary,
      todayTextColor: colors.error,
      selectedDayBackgroundColor: colors.primary,
      selectedDayTextColor: colors.onPrimary,
      dayTextColor: colors.text,
      textDisabledColor: colors.border,
      textDayFontSize: (typography.body.fontSize as number) || 16,
      textDayFontWeight: 500,
      textMonthFontWeight: 700,
      textMonthFontSize: (typography.h2.fontSize as number) || 24,
      textDayHeaderFontSize: 12,
    }),
    [colors, typography],
  );

  const onDayPress = (day: DateData) => {
    setSelected(day.dateString);
    setModalVisible(true);
  };

  const onMonthChange = (month: { year: number; month: number }) => {
    setCurrentYear(month.year);
    setCurrentMonth(month.month);
  };

  return (
    <View style={[styles.container, { backgroundColor: colors.background, padding: spacing.m }]}>
      <Calendar
        onDayPress={onDayPress}
        onMonthChange={onMonthChange}
        hideExtraDays
        markedDates={markedDates}
        theme={calendarTheme as any}
        enableSwipeMonths
        firstDay={1}
      />

      <Modal
        visible={modalVisible}
        transparent
        animationType="slide"
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { backgroundColor: colors.surface }]}>
            <View style={styles.modalHeader}>
              <Text style={[typography.h2, { color: colors.text }]}>{selected}</Text>
              <TouchableOpacity onPress={() => setModalVisible(false)}>
                <Text style={[typography.body, { color: colors.primary }]}>Fechar</Text>
              </TouchableOpacity>
            </View>
            <ScrollView style={styles.modalBody}>
              {diaData?.detalhes?.map((item, idx) => (
                <View key={idx} style={styles.detailItem}>
                  <Text style={[typography.body, { color: colors.text, fontWeight: 'bold' }]}>
                    {item.nome_fantasia}
                  </Text>
                  <Text style={[typography.caption, { color: colors.placeholder }]}>
                    CNPJ: {item.cnpj}
                  </Text>
                  <Text style={[typography.body, { color: item.tipo === 'PAGAR' ? colors.error : colors.secondary }]}>
                    {formatCurrencyBRL(item.valor)} ({item.tipo || 'N/A'})
                  </Text>
                </View>
              )) || (
                <Text style={[typography.body, { color: colors.placeholder }]}>Sem lançamentos</Text>
              )}
            </ScrollView>
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    width: '90%',
    maxHeight: '70%',
    borderRadius: 8,
    padding: 16,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  modalBody: {
    flex: 1,
  },
  detailItem: {
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
});

export default CalendarScreen;
