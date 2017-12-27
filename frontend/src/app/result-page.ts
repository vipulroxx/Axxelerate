import { Result } from './result'

export interface ResultPage {
  prevFrom : string,
  nextFrom : string,
  results : [Result]
}
