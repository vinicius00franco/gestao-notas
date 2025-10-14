import React from 'react';
import { VictoryBar, VictoryChart, VictoryAxis, VictoryTheme } from 'victory-native';
import Card from '@/components/Card';
import { useTheme } from '@/theme/ThemeProvider';

type BarData = { x: string | number; y: number };

type Props = {
  title?: string;
  data: BarData[];
  height?: number;
};

export default function BarChartCard({
  title,
  data,
  height = 220,
}: Props) {
  const theme = useTheme();
  return (
    <Card title={title}>
      <VictoryChart height={height} domainPadding={{ x: 20 }} padding={{ top: 10, bottom: 40, left: 40, right: 16 }} theme={VictoryTheme.material}>
        <VictoryAxis style={{ tickLabels: { fontSize: 10, fill: theme.colors.onSurfaceVariant } }} />
        <VictoryAxis dependentAxis style={{ tickLabels: { fontSize: 10, fill: theme.colors.onSurfaceVariant } }} />
        <VictoryBar data={data} style={{ data: { fill: theme.colors.primary } }} />
      </VictoryChart>
    </Card>
  );
}