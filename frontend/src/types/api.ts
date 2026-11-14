export type Quality = 'ok' | 'missing' | 'interpolated'

export interface Variable {
  variableId: string
  name: string
  description: string
  unit: string
  source: string
  category: string
  minYears: number
}

export interface BBox {
  latMin: number
  latMax: number
  lonMin: number
  lonMax: number
}

export interface Region {
  regionId: string
  name: string
  bbox: BBox
  description: string
  type: 'predefined' | 'custom'
}

export interface TimeSeriesPoint {
  seriesId: string
  variableId: string
  regionId: string
  date: string // primer día del mes UTC, ISO 8601
  value: number | null // null solo si quality === 'missing'
  quality: Quality
}

export interface TrendAnalysis {
  analysisId: string
  variableId: string
  regionId: string
  startDate: string
  endDate: string
  slope: number // unidad de la variable por año
  pValue: number
  significant: boolean
  interpretation: string
  createdAt: string
}

export interface SeriesData {
  variable: Variable
  region: Region
  timeSeries: TimeSeriesPoint[]
  trendAnalysis: TrendAnalysis | null
}

export interface SeriesQuery {
  variableId: string
  regionId: string
  startDate: string
  endDate: string
}

export interface ApiErrorBody {
  error: {
    code: string
    message: string
    details?: Record<string, unknown>
    requestId?: string
  }
}