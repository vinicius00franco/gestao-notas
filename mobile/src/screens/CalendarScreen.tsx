import { useTheme } from '@/theme/ThemeProvider';
import { useMemo, useState } from 'react';
import { ActivityIndicator, ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { Calendar, LocaleConfig } from 'react-native-calendars';
import { CalendarDiaItem } from '../api/services/calendarService';
import { useCalendarDia, useCalendarResumo, useContasAPagar, useContasAReceber } from '../hooks/api';
import { Lancamento } from '../types';
import { formatCurrencyBRL } from '../utils/format';

LocaleConfig.locales['pt-br'] = {
  monthNames: ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'],
  monthNamesShort: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
  dayNames: ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'],
  dayNamesShort: ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'],
  today: 'Hoje',
};
LocaleConfig.defaultLocale = 'pt-br';

type DateData = { dateString: string; day: number; month: number; year: number; timestamp: number };
type MarkedDates = Record<string, any>;

const LancamentoCalendarItem = ({ item, colors, typography }: { item: CalendarDiaItem; colors: any; typography: any }) => {
  const isPagar = item.tipo === 'PAGAR';
  return (
    <View style={[styles.detailItem, { borderBottomColor: colors.border }]}>
      <Text style={[typography.body, { color: colors.text, fontWeight: 'bold' }]}>{item.nome_fantasia}</Text>
      <Text style={[typography.body, { color: isPagar ? colors.error : colors.secondary }]}>
        {formatCurrencyBRL(item.valor)}
      </Text>
    </View>
  );
};

const LancamentoMesItem = ({ item, colors, typography }: { item: Lancamento; colors: any; typography: any }) => {
    const isPagar = item.clf_tipo.nome === 'A Pagar';
    return (
      <View style={[styles.detailItem, { borderBottomColor: colors.border }]}>
        <Text style={[typography.body, { color: colors.text, fontWeight: 'bold' }]}>{item.descricao} ({item.data_vencimento})</Text>
        <Text style={[typography.body, { color: isPagar ? colors.error : colors.secondary }]}>
          {formatCurrencyBRL(item.valor)}
        </Text>
      </View>
    );
  };

const CalendarScreen = () => {
  const { colors, spacing, typography } = useTheme();
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [currentYear, setCurrentYear] = useState<number>(new Date().getFullYear());
  const [currentMonth, setCurrentMonth] = useState<number>(new Date().getMonth() + 1);

  const { data: resumoData } = useCalendarResumo(currentYear, currentMonth);
  const { data: diaData, isLoading: isLoadingDia } = useCalendarDia(selectedDate || '');

  const { data: contasAPagar } = useContasAPagar();
  const { data: contasAReceber } = useContasAReceber();
  const detalhesDoMes = useMemo(() => [...(contasAPagar || []), ...(contasAReceber || [])].sort((a,b) => a.data_vencimento.localeCompare(b.data_vencimento)), [contasAPagar, contasAReceber]);

  const markedDates: MarkedDates = useMemo(() => {
    const marks: MarkedDates = {};

    resumoData?.dias.forEach((diaInfo) => {
      const dateString = diaInfo.data;
      const saldo = (diaInfo.valor_receber ?? 0) - (diaInfo.valor_pagar ?? 0);
      marks[dateString] = {
        marked: true,
        dotColor: saldo > 0 ? colors.secondary : colors.error,
      };
    });

    if (selectedDate) {
      marks[selectedDate] = {
        ...marks[selectedDate],
        selected: true,
        selectedColor: colors.primary,
      };
    }

    return marks;
  }, [resumoData, selectedDate, colors]);

  const calendarTheme = useMemo(() => ({
    calendarBackground: colors.background,
    monthTextColor: colors.text,
    textSectionTitleColor: colors.placeholder,
    arrowColor: colors.primary,
    todayTextColor: colors.primary,
    dayTextColor: colors.text,
    textDisabledColor: colors.border,
  }), [colors]);

  const onDayPress = (day: DateData) => {
    setSelectedDate(day.dateString);
  };

  const onMonthChange = (month: { year: number; month: number }) => {
    setSelectedDate(null); // Reseta a seleção ao mudar de mês
    setCurrentYear(month.year);
    setCurrentMonth(month.month);
  };

  const renderDetailContent = () => {
    if (selectedDate) {
      if (isLoadingDia) return <ActivityIndicator color={colors.primary} />;
      return (
        <>
          <View style={styles.detailHeader}>
            <Text style={[typography.h2, { color: colors.text }]}>Detalhes de {selectedDate}</Text>
            <TouchableOpacity onPress={() => setSelectedDate(null)}>
              <Text style={{ color: colors.primary }}>Visão do Mê</Text>
            </TouchableOpacity>
          </View>
          {diaData?.detalhes?.map((item, index) => <LancamentoCalendarItem key={index} item={item} colors={colors} typography={typography} />)}
        </>
      );
    }

    return (
      <>
        <Text style={[typography.h2, { color: colors.text, marginBottom: spacing.s }]}>Lançamentos do Mês</Text>
        {detalhesDoMes.map(item => <LancamentoMesItem key={item.uuid} item={item} colors={colors} typography={typography} />)}
      </>
    );
  };

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <View style={{ padding: spacing.m }}>
        <Calendar
          onDayPress={onDayPress}
          onMonthChange={onMonthChange}
          markedDates={markedDates}
          theme={calendarTheme as any}
          enableSwipeMonths
          firstDay={1}
        />
      </View>
      <View style={[styles.detailContainer, { backgroundColor: colors.surface, padding: spacing.m }]}>
        <ScrollView>
          {renderDetailContent()}
        </ScrollView>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  detailContainer: {
    flex: 1,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
  },
  detailHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    flex: 1,
    alignItems: 'center',
    marginBottom: 16,
    flexWrap: 'wrap',
  },
  detailItem: {
    paddingVertical: 12,
    borderBottomWidth: 1,
  },
});

export default CalendarScreen;
