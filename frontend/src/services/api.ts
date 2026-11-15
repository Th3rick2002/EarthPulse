import axios, { isAxiosError } from 'axios'
import type {
  ApiErrorBody,
  AreaSeriesResult,
  CompareSeriesQuery,
  Region,
  SeriesData,
  SeriesQuery,
  VariableAvailability,
  Variable,
} from '../types/api'

const baseURL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

const http = axios.create({
  baseURL: `${baseURL}/api/v1`,
  timeout: 60_000,
})

export class ApiError extends Error {
  code: string
  status: number | null
  requestId?: string
  diagnostic?: string

  constructor(
    message: string,
    code: string,
    status: number | null,
    requestId?: string,
    diagnostic?: string,
  ) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.status = status
    this.requestId = requestId
    this.diagnostic = diagnostic
  }
}

export function asApiError(e: unknown): ApiError {
  if (e instanceof ApiError) return e
  if (isAxiosError<ApiErrorBody>(e)) {
    const body = e.response?.data?.error
    if (body) {
      return new ApiError(
        translateError(body.code, body.message),
        body.code,
        e.response?.status ?? null,
        body.requestId,
        diagnosticMessage(body.details),
      )
    }
    if (e.code === 'ECONNABORTED') {
      return new ApiError(
        'La consulta tardó demasiado. Intenta de nuevo.',
        'TIMEOUT',
        null,
      )
    }
    if (!e.response) {
      return new ApiError(
        'No se pudo conectar con el servidor.',
        'NETWORK_ERROR',
        null,
      )
    }
    return new ApiError(
      `El servidor respondió con error ${e.response.status}.`,
      'HTTP_ERROR',
      e.response.status,
    )
  }
  return new ApiError('Ocurrió un error inesperado.', 'UNKNOWN', null)
}

function diagnosticMessage(details?: Record<string, unknown>): string | undefined {
  const message = details?.upstreamMessage
  const status = details?.upstreamStatus
  const availableEndDate = details?.availableEndDate
  if (typeof message === 'string') {
    return typeof status === 'number' ? `Meteomatics respondió ${status}: ${message}` : message
  }
  if (typeof availableEndDate === 'string') return `Datos disponibles hasta ${availableEndDate}.`
  return undefined
}

function translateError(code: string, message: string) {
  if (code === 'PROVIDER_TIMEOUT' || /request timed out/i.test(message)) {
    return 'La fuente de datos tardó demasiado en responder. Puedes intentarlo de nuevo.'
  }
  if (code === 'PROVIDER_UNAVAILABLE' && /credentials/i.test(message)) {
    return 'La fuente meteorológica no está lista. Pide a una persona administradora que revise su configuración.'
  }
  if (code === 'PROVIDER_UNAVAILABLE') {
    return 'Esta fuente de datos no está disponible en este momento. Inténtalo más tarde.'
  }
  if (code === 'PROVIDER_ERROR') {
    return 'No pudimos obtener los datos de la fuente científica. Inténtalo de nuevo.'
  }
  if (code === 'NOT_FOUND') {
    return 'No encontramos esa opción en el catálogo. Actualiza la página e inténtalo de nuevo.'
  }
  if (code === 'INVALID_PARAMS') {
    if (/outside the provider's available precipitation dates/i.test(message)) {
      return 'Ese periodo incluye meses de lluvia que la fuente todavía no ha publicado. Elige un mes anterior al último disponible.'
    }
    return 'Revisa el periodo elegido. Las fechas deben ser válidas y cubrir meses completos.'
  }
  return 'No pudimos completar la consulta. Inténtalo de nuevo.'
}

export async function getVariableAvailability(variableId: string): Promise<VariableAvailability> {
  try {
    const { data } = await http.get<{ data: VariableAvailability }>(`/availability`, {
      params: { variableId },
    })
    return data.data
  } catch (e) {
    throw asApiError(e)
  }
}

export async function getVariables(): Promise<Variable[]> {
  try {
    const { data } = await http.get<{ data: Variable[] }>('/variables')
    return data.data
  } catch (e) {
    throw asApiError(e)
  }
}

export async function getRegions(): Promise<Region[]> {
  try {
    const { data } = await http.get<{ data: Region[] }>('/regions')
    return data.data
  } catch (e) {
    throw asApiError(e)
  }
}

export async function getSeries(query: SeriesQuery): Promise<SeriesData> {
  try {
    const response = await http.get<{ data: SeriesData | { jobId: string; status: string } }>('/series', {
      params: query,
    })
    if (response.status !== 202) return response.data.data as SeriesData

    const job = response.data.data as { jobId: string; status: string }
    const deadline = Date.now() + 15 * 60_000
    while (Date.now() < deadline) {
      await new Promise((resolve) => setTimeout(resolve, 2_000))
      const result = await http.get<{
        data: SeriesData | { jobId: string; status: string }
      }>(`/series/jobs/${job.jobId}`, {
        validateStatus: (status) => status === 200 || status === 202,
      })
      if (result.status === 200) return result.data.data as SeriesData
    }
    throw new ApiError(
      'La consulta sigue procesándose. Vuelve a intentarlo en unos minutos.',
      'JOB_TIMEOUT',
      null,
    )
  } catch (e) {
    throw asApiError(e)
  }
}

export async function compareAreas(query: CompareSeriesQuery): Promise<AreaSeriesResult[]> {
  try {
    const response = await http.post<{ data: { jobId: string; status: string } | { results: AreaSeriesResult[] } }>(
      '/series/compare',
      query,
    )
    if (response.status !== 202) {
      return (response.data.data as { results: AreaSeriesResult[] }).results
    }

    const job = response.data.data as { jobId: string; status: string }
    const deadline = Date.now() + 30 * 60_000
    while (Date.now() < deadline) {
      await new Promise((resolve) => setTimeout(resolve, 2_000))
      const result = await http.get<{ data: { jobId: string; status: string } | { results: AreaSeriesResult[] } }>(
        `/series/jobs/${job.jobId}`,
        { validateStatus: (status) => status === 200 || status === 202 },
      )
      if (result.status === 200) {
        return (result.data.data as { results: AreaSeriesResult[] }).results
      }
    }
    throw new ApiError(
      'La comparación sigue procesándose. Puedes esperar un poco más e intentarlo de nuevo después.',
      'JOB_TIMEOUT',
      null,
    )
  } catch (error) {
    throw asApiError(error)
  }
}
