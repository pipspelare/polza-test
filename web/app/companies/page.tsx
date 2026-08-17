import Link from "next/link";
import { pool } from "../../lib/db";
import styles from "./companies.module.css";

type Company = {
  id: string;
  name: string;
  category: string;
  city: string;
  address: string | null;
  rating: number | null;
  reviews_count: number;
  site: string | null;
  phone: string | null;
};

type SearchParams = {
  q?: string | string[];
  city?: string | string[];
};

function getParam(value: string | string[] | undefined): string {
  if (Array.isArray(value)) {
    return value[0] ?? "";
  }

  return value ?? "";
}

async function getCities(): Promise<string[]> {
  const result = await pool.query<{ city: string }>(`
    SELECT DISTINCT city
    FROM companies
    ORDER BY city
  `);

  return result.rows.map((row) => row.city);
}

async function getCompanies(
  query: string,
  city: string,
): Promise<Company[]> {
  const result = await pool.query<Company>(
    `
      SELECT
        id,
        name,
        category,
        city,
        address,
        rating::float8 AS rating,
        reviews_count,
        site,
        phone
      FROM companies
      WHERE
        ($1 = '' OR name ILIKE '%' || $1 || '%')
        AND ($2 = '' OR city = $2)
      ORDER BY name
      LIMIT 100
    `,
    [query, city],
  );

  return result.rows;
}

export default async function CompaniesPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const params = await searchParams;
  const query = getParam(params.q).trim();
  const city = getParam(params.city).trim();

  const [companies, cities] = await Promise.all([
    getCompanies(query, city),
    getCities(),
  ]);

  return (
    <main className={styles.page}>
      <div className={styles.container}>
        <Link className={styles.backLink} href="/">
          ← На главную
        </Link>

        <div className={styles.header}>
          <div>
            <p className={styles.eyebrow}>PostgreSQL directory</p>
            <h1>Компании</h1>
            <p className={styles.subtitle}>
              Найдено записей: {companies.length}
            </p>
          </div>
        </div>

        <form className={styles.filters} method="GET">
          <label>
            Название
            <input
              name="q"
              defaultValue={query}
              placeholder="Например, Прайм"
            />
          </label>

          <label>
            Город
            <select name="city" defaultValue={city}>
              <option value="">Все города</option>
              {cities.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>

          <button type="submit">Найти</button>

          <Link className={styles.reset} href="/companies">
            Сбросить
          </Link>
        </form>

        <div className={styles.tableWrapper}>
          <table className={styles.table}>
	  <thead>
              <tr>
                <th>Компания</th>
                <th>Категория</th>
                <th>Город</th>
                <th>Рейтинг</th>
                <th>Отзывы</th>
                <th>Сайт</th>
              </tr>
            </thead>

            <tbody>
              {companies.map((company) => (
                <tr key={company.id}>
                  <td>
                    <div className={styles.companyName}>
                      {company.name}
                    </div>
                    <div className={styles.companyId}>
                      {company.id}
                    </div>
                  </td>
                  <td>{company.category}</td>
                  <td>{company.city}</td>
                  <td>
                    {company.rating === null
                      ? "—"
                      : company.rating.toFixed(1)}
                  </td>
                  <td>{company.reviews_count}</td>
                  <td>
                    {company.site ? (
                      <a
			  className={styles.siteLink}
			  href={company.site}
			  target="_blank"
			  rel="noreferrer"
			>
			  Открыть
			</a>
		    ) : (
                      "—"
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {companies.length === 0 && (
            <div className={styles.empty}>
              По заданным фильтрам компании не найдены.
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
