import React from 'react';
import { VictoryBar, VictoryChart, VictoryAxis, VictoryStack, VictoryTheme } from 'victory-native';
import Card from '@/components/Card';
import { useTheme } from '@/theme/ThemeProvider';

type Series = { data: { x: string | number; y: number }[]; color: string };

type Props = {
  title?: string;
  series: Series[];
  categories?: (string | number)[];
  height?: number;
};

export default function StackedBarChartCard({
  title = 'Sales by Month and Region',
  series,
  categories,
  height = 220,
}: Props) {
  const theme = useTheme();
  return (
    <Card title={title}>
      <VictoryChart height={height} padding={{ top: 10, bottom: 40, left: 40, right: 16 }} theme={VictoryTheme.material}>
        <VictoryAxis tickValues={categories} style={{ tickLabels: { fontSize: 10, fill: theme.colors.onSurfaceVariant } }} />
        <VictoryAxis dependentAxis style={{ tickLabels: { fontSize: 10, fill: theme.colors.onSurfaceVariant } }} />
        <VictoryStack>
          {series.map((s, idx) => (
            <VictoryBar key={idx} data={s.data} style={{ data: { fill: s.color } }} />
          ))}
        </VictoryStack>
      </VictoryChart>
    </Card>
  );
}
