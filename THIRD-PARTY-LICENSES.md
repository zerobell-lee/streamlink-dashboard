# Third-Party Licenses

This document contains the licenses for all third-party software used in this project.

## Project License

Streamlink Dashboard is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## Backend Dependencies

### Core Framework Dependencies

**FastAPI** - MIT License  
Copyright (c) 2018 Sebastián Ramírez  
Used under MIT License

**SQLAlchemy** - MIT License  
Copyright (c) 2006-2023 SQLAlchemy authors  
Used under MIT License

**APScheduler** - MIT License  
Copyright (c) Python Software Foundation  
Used under MIT License

**Streamlink** - Apache License 2.0  
Used under Apache License 2.0

### Notable Backend Dependencies with Different Licenses

**pycountry** - GNU Lesser General Public License v2 (LGPLv2)  
Used for country code handling. LGPL v2 is compatible with MIT for dynamic linking.

**certifi** - Mozilla Public License 2.0 (MPL 2.0)  
Used for SSL certificate verification. MPL 2.0 is compatible with MIT.

## Frontend Dependencies

### Core Framework Dependencies

**Next.js** - MIT License  
Copyright (c) 2016-present Vercel, Inc.  
Used under MIT License

**React** - MIT License  
Copyright (c) Meta Platforms, Inc. and affiliates.  
Used under MIT License

**Tailwind CSS** - MIT License  
Copyright (c) Tailwind Labs, Inc.  
Used under MIT License

### UI Component Libraries

**@headlessui/react** - MIT License  
Copyright (c) Tailwind Labs, Inc.  
Used under MIT License

**Lucide React** - ISC License  
Copyright (c) Lucide Contributors  
Used under ISC License (compatible with MIT)

**Recharts** - MIT License  
Copyright (c) 2015-2023 Recharts Group  
Used under MIT License

### Notable Frontend Dependencies with Different Licenses

**Sharp (libvips components)** - LGPL-3.0-or-later  
- @img/sharp-libvips-linux-x64: LGPL-3.0-or-later
- @img/sharp-libvips-linuxmusl-x64: LGPL-3.0-or-later

Used for image processing. LGPL v3 allows dynamic linking with MIT licensed software.
The Sharp library itself is Apache-2.0 licensed, only the underlying libvips components use LGPL.

**axe-core** - MPL-2.0  
Used for accessibility testing. MPL 2.0 is compatible with MIT.

**caniuse-lite** - CC-BY-4.0  
Used for browser compatibility data. Creative Commons license for data only.

## License Compatibility Summary

| License Type | Count | Compatibility | Notes |
|--------------|-------|---------------|--------|
| MIT | 200+ | ✅ Compatible | Perfect compatibility |
| Apache-2.0 | 30+ | ✅ Compatible | Compatible with MIT |
| BSD (all variants) | 20+ | ✅ Compatible | Compatible with MIT |
| ISC | 15+ | ✅ Compatible | Compatible with MIT |
| LGPL v2/v3 | 3 | ✅ Compatible* | *For dynamic linking only |
| MPL 2.0 | 2 | ✅ Compatible | Compatible with MIT |
| CC-BY-4.0 | 1 | ✅ Compatible | Data license only |

## Attribution Requirements

This software includes dependencies under various open source licenses:

- **MIT License**: Requires copyright notice and license text inclusion
- **Apache License 2.0**: Requires copyright notice and license text inclusion  
- **BSD Licenses**: Require copyright notice and disclaimer inclusion
- **ISC License**: Requires copyright notice inclusion
- **LGPL**: Requires source availability for LGPL components (handled by package managers)
- **MPL 2.0**: Requires source availability for modified MPL files

## Full License Texts

### Backend Dependencies License Report

For complete backend dependency license information, run:
```bash
cd backend
pip-licenses --format=markdown
```

### Frontend Dependencies License Report

For complete frontend dependency license information, run:
```bash
cd frontend
npx license-checker --markdown
```

## Compliance Statement

This project has been reviewed for license compatibility and is suitable for open source distribution under the MIT License. All dependencies are either MIT-compatible or use licenses that allow combination with MIT-licensed software.

**Date of Review**: September 4, 2025  
**Reviewed By**: Streamlink Dashboard Development Team  
**Status**: ✅ Compliant for Open Source Release

## Questions or Concerns

If you have questions about the licensing of this software or its dependencies, please:

1. Check this document for basic compatibility information
2. Review the original license files in the respective package directories
3. Open an issue on the project repository for specific questions

---

*This document is provided for informational purposes. Please consult with appropriate legal counsel for specific licensing questions.*