import axios, { isAxiosError } from 'axios'
import type {
  ApiErrorBody,
  Region,
  SeriesData,
  SeriesQuery,
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

  constructor(
    message: string,
    code: string,
    status: number | null,
    requestId?: string,
  ) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.status = status
    this.requestId = requestId
  }
}

export function asApiError(e: unknown): ApiError {
  if (e instanceof ApiError) return e
  if (isAxiosError<ApiErrorBody>(e)) {
    const body = e.response?.data?.error
    if (body) {
      return new ApiError(
        body.message,
        body.code,
        e.response?.status ?? null,
        body.requestId,
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
    const { data } = await http.get<{ data: SeriesData }>('/series', {
      params: query,
    })
    return data.data
  } catch (e) {
    throw asApiError(e)
  }
}