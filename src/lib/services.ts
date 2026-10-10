import rawData from '../../data/services.json';

export type CategoryKey = keyof typeof rawData.categories;
export type ServiceKey = keyof typeof rawData.services;
export type CopyPart = string | { kind: 'included-images'; suffix: string } | { kind: 'content-ref'; index: number } | { kind: 'duration-hours'; prefix: string; suffix: string };
export type BookingTermKind = 'cancellation' | 'late-arrival' | 'weather' | 'deposit' | 'deposit-refund' | 'balance' | 'gallery' | 'delivery' | 'included-images';

export interface Service {
  name: string; price: number; included_images: number | null; category: CategoryKey;
  from_price: boolean; max_price: number | null; content: CopyPart[];
  landing_content?: CopyPart[]; duration_hours?: number;
}
export interface ServicesData {
  schema_version: 2; currency: 'NOK'; categories: Record<CategoryKey, string>;
  services: Record<ServiceKey, Service>;
  booking_groups: Array<{ label: string; services: ServiceKey[] }>;
  restoration: {
    simple: { price: number; label: string };
    standard: { price: number; label: string };
    advanced: { price: number; label: string };
  };
  extras: { person: { price: number }; time: { price: number; minutes: number }; travel: { price: number; included_mil: number; origin: string }; express: { price: number; hours: number } };
  digital: { mobile: { price: number }; high_resolution: { price: number }; full_resolution: { price: number }; complete: { price: number; scope: string; separately_quoted: string } };
  rules: { deposit_percent: number; balance_percent: number; delivery_min_weeks: number; delivery_max_weeks: number; cancellation_notice_hours: number; late_minutes: number; deposit_refund_clause: string; weather_policy: string; gallery_provider: string; copy: Record<string, never>; booking_terms: BookingTermKind[] };
}

function integer(value: unknown, label: string, minimum = 0): asserts value is number {
  if (!Number.isInteger(value) || (value as number) < minimum) throw new TypeError(`${label} must be an integer >= ${minimum}`);
}
function text(value: unknown, label: string): asserts value is string {
  if (typeof value !== 'string' || !value.trim()) throw new TypeError(`${label} must contain text`);
}
function validatePart(part: unknown, label: string): asserts part is CopyPart {
  if (typeof part === 'string') { if (!part.trim() || part.includes('{{')) throw new TypeError(`${label} must contain plain copy`); return; }
  if (!part || typeof part !== 'object' || !('kind' in part)) throw new TypeError(`${label} is invalid`);
  const value = part as Record<string, unknown>;
  if (value.kind === 'included-images') { if (typeof value.suffix !== 'string') throw new TypeError(`${label}.suffix is invalid`); }
  else if (value.kind === 'content-ref') integer(value.index, `${label}.index`);
  else if (value.kind === 'duration-hours') { if (typeof value.prefix !== 'string' || typeof value.suffix !== 'string') throw new TypeError(`${label} duration copy is invalid`); }
  else throw new TypeError(`${label}.kind is invalid`);
}
export function validateServicesData(value: unknown): asserts value is ServicesData {
  if (!value || typeof value !== 'object') throw new TypeError('Service data must be an object');
  const data = value as ServicesData;
  if (data.schema_version !== 2 || data.currency !== 'NOK') throw new TypeError('Unsupported schema or currency');
  if (!data.services || !Object.keys(data.services).length) throw new TypeError('At least one service is required');
  for (const [key, service] of Object.entries(data.services)) {
    if (!service.name?.trim() || !(service.category in data.categories)) throw new TypeError(`Missing name or unknown category: ${key}`);
    integer(service.price, `${key}.price`);
    if (typeof service.from_price !== 'boolean') throw new TypeError(`${key}.from_price must be boolean`);
    if (service.max_price !== null) integer(service.max_price, `${key}.max_price`, service.price);
    if (service.included_images !== null) integer(service.included_images, `${key}.included_images`);
    if (!Array.isArray(service.content) || !service.content.length) throw new TypeError(`Missing package contents: ${key}`);
    service.content.forEach((part, index) => validatePart(part, `${key}.content.${index}`));
    service.landing_content?.forEach((part, index) => validatePart(part, `${key}.landing_content.${index}`));
  }
  integer(data.extras.person.price, 'extras.person.price');
  integer(data.extras.time.price, 'extras.time.price'); integer(data.extras.time.minutes, 'extras.time.minutes', 1);
  integer(data.extras.travel.price, 'extras.travel.price'); integer(data.extras.travel.included_mil, 'extras.travel.included_mil'); text(data.extras.travel.origin, 'extras.travel.origin');
  integer(data.extras.express.price, 'extras.express.price'); integer(data.extras.express.hours, 'extras.express.hours', 1);
  integer(data.digital.mobile.price, 'digital.mobile.price'); integer(data.digital.high_resolution.price, 'digital.high_resolution.price');
  integer(data.digital.full_resolution.price, 'digital.full_resolution.price'); integer(data.digital.complete.price, 'digital.complete.price');
  text(data.digital.complete.scope, 'digital.complete.scope'); text(data.digital.complete.separately_quoted, 'digital.complete.separately_quoted');
  for (const [key, tier] of Object.entries(data.restoration)) {
    integer(tier.price, `restoration.${key}.price`);
    text(tier.label, `restoration.${key}.label`);
  }
  integer(data.rules.deposit_percent, 'deposit_percent'); integer(data.rules.balance_percent, 'balance_percent');
  if (data.rules.deposit_percent + data.rules.balance_percent !== 100) throw new TypeError('Deposit and balance must sum to 100');
  for (const key of ['delivery_min_weeks','delivery_max_weeks','cancellation_notice_hours','late_minutes'] as const) integer(data.rules[key], key, 1);
  if (data.rules.delivery_max_weeks < data.rules.delivery_min_weeks) throw new TypeError('Invalid delivery range');
  text(data.rules.deposit_refund_clause, 'deposit_refund_clause'); text(data.rules.weather_policy, 'weather_policy'); text(data.rules.gallery_provider, 'gallery_provider');
  const offered = data.booking_groups.flatMap((group) => group.services);
  if (offered.length !== new Set(offered).size || offered.length !== Object.keys(data.services).length || offered.some((key) => !(key in data.services))) throw new TypeError('Each service must appear once in booking groups');
  const allowed = new Set<BookingTermKind>(['cancellation','late-arrival','weather','deposit','deposit-refund','balance','gallery','delivery','included-images']);
  if (data.rules.booking_terms.length !== allowed.size || data.rules.booking_terms.some((term) => !allowed.has(term))) throw new TypeError('Booking terms are invalid');
}

validateServicesData(rawData);
export const data: ServicesData = rawData;
export function grouped(value: number): string { return new Intl.NumberFormat('nb-NO', { useGrouping: true, maximumFractionDigits: 0 }).format(value).replace(/\u00a0/g, ' '); }
export function formatImages(value: number | null, booking = false): string { if (value === null) throw new TypeError('Image count is required'); return booking ? `${value} ${value === 1 ? 'bilde' : 'bilder'}` : `${value} ${value === 1 ? 'digitalt bilde' : 'digitale bilder'}`; }
export function formatPrice(service: Service, options: { group?: boolean; lower?: boolean } = {}): string {
  const number = options.group || service.price >= 10000 ? grouped(service.price) : String(service.price);
  const maximum = service.max_price === null ? '' : `–${options.group || service.max_price >= 10000 ? grouped(service.max_price) : service.max_price}`;
  return `${service.from_price ? (options.lower ? 'fra ' : 'Fra ') : ''}${number}${maximum}`;
}
export function serviceContent(service: Service, collection: 'content' | 'landing_content', index: number): string {
  const part = service[collection]?.[index]; if (part === undefined) throw new TypeError(`Missing ${collection}.${index}`);
  if (typeof part === 'string') return part;
  if (part.kind === 'included-images') { if (service.included_images === null) throw new TypeError('Included-image copy requires an image count'); return formatImages(service.included_images) + part.suffix; }
  if (part.kind === 'content-ref') return serviceContent(service, 'content', part.index);
  if (service.duration_hours === undefined) throw new TypeError('Duration copy requires duration_hours');
  return `${part.prefix}${service.duration_hours}${part.suffix}`;
}
export function bookingTerms(source: ServicesData = data): string[] {
  const r = source.rules;
  const terms: Record<BookingTermKind, string> = {
    cancellation: `Gi beskjed minst ${r.cancellation_notice_hours} timer før ved avbestilling eller endring.`,
    'late-arrival': `Ved mer enn ${r.late_minutes} minutters forsinkelse kan fotograferingen forkortes eller flyttes.`, weather: r.weather_policy,
    deposit: `Booking bekreftes først etter skriftlig bekreftelse og betaling av ${r.deposit_percent} % forskudd.`,
    'deposit-refund': `Forskuddet reserverer ønsket dato, trekkes fra fotograferingsprisen og ${r.deposit_refund_clause}.`,
    balance: `De resterende ${r.balance_percent} % betales via FotoSky etter fotograferingen og før privatgalleriet åpnes.`,
    gallery: 'Når restbeløpet er betalt, åpnes galleriet. Eventuelle tilleggskjøp kommer i tillegg.',
    delivery: `Leveringstid er normalt ${r.delivery_min_weeks}–${r.delivery_max_weeks} uker via privat galleri.`,
    'included-images': 'Kun antallet digitale bilder som står oppført for pakken er inkludert. Flere bilder og fulloppløselige filer kjøpes separat.'
  };
  return r.booking_terms.map((kind) => terms[kind]);
}
export function derived(source: ServicesData = data) { const s = source.services; return {
  pets_range: `${Math.min(s['pet-mini'].price,s['pet-standard'].price,s['pet-premium'].price)}-${Math.max(s['pet-mini'].price,s['pet-standard'].price,s['pet-premium'].price)}`,
  portrait_family_range: `${Math.min(s.portrait.price,s.family.price)}-${Math.max(s.portrait.price,s.family.price)}`,
  family_low: Math.min(s.portrait.price,s.family.price,s.basic.price,s.favorite.price,s.total.price), family_high: Math.max(s.portrait.price,s.family.price,s.basic.price,s.favorite.price,s.total.price),
  wedding_price: `${s.wedding.price}${s.wedding.from_price ? '+' : ''}` } }
export function bookingLabel(service: Service): string { let label = `${service.name}${service.max_price === null ? ' – ' : ', '}${formatPrice(service,{lower:true})} kr`; if (service.included_images !== null) label += ` – ${formatImages(service.included_images,true)} inkludert`; return label; }
export function json(value: unknown): string { return JSON.stringify(String(value)).replace(/</g, '\\u003c'); }
